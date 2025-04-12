import os
import re
import discord
import json
import random
import datetime
from dateutil.parser import parse
from discord.ext import commands
from dotenv import load_dotenv
import technical_analysis
import option_calculator
import unusual_activity
import combined_scalp_stop_loss
import calculate_dynamic_theta_decay

# Load environment variables
load_dotenv()

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default config if not exists
        default_config = {
            "channel_whitelist": [],
            "admin_users": []
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

config = load_config()

class OptionsBotNLP:
    """Natural language processor for options trading queries"""
    
    def __init__(self):
        # Common words to exclude from ticker detection
        self.common_words = ['WHAT', 'WILL', 'THE', 'FOR', 'ARE', 'OPTIONS', 'OPTION', 'CALLS', 'PUTS', 
                            'STRIKE', 'PRICE', 'BE', 'WORTH', 'HOW', 'MUCH', 'CAN', 'YOU', 'TELL', 'ME', 
                            'ABOUT', 'PREDICT', 'CALCULATE', 'ESTIMATE', 'SHOW', 'GET', 'BUY', 'SELL', 
                            'CALL', 'PUT', 'AND', 'WITH', 'ANALYZE', 'UNUSUAL', 'ACTIVITY', 'STOP', 'LOSS']
        
        # Enhanced regex patterns for extracting information from queries
        self.ticker_pattern = r'(?:\bfor\s+)?(?:\bmy\s+)?([A-Z]{1,5})\b'
        self.strike_pattern = r'(?:\$?(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s?(?:strike|[$]))'
        self.expiry_pattern = r'(?:(?:expir(?:ing|e|es|ation)?\s+(?:on|at|in)?\s+)?(\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4}|\w+\s+\d{1,2}(?:st|nd|rd|th)?|\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|\d{1,2}(?:st|nd|rd|th)?\s+\w+))'
        self.option_type_pattern = r'\b(call|put)s?\b'
        self.contract_count_pattern = r'(?:my)\s+(\d+)\s+(?:[a-zA-Z]+\s+)*(?:contracts?|positions?|options?)|(?:what\s+will\s+my)\s+(\d+)\s+(?:[a-zA-Z]+\s+)*(?:contracts?|positions?|options?)|(?:I\s+(?:have|own|bought|purchased)|with|for)\s+(\d+)\s+(?:[a-zA-Z]+\s+)*(?:contracts?|positions?|options?)|(\d+)\s+(?:contracts?|positions?|options?)'
        self.price_target_pattern = r'(?:target|reach(?:es)?|go(?:es)? to|hits?|move(?:s)? to)\s+(?:price\s+(?:of\s+)?)?\$?(\d+\.?\d*)'
        
        # Enhanced request type patterns
        self.request_type_patterns = {
            'price': r'\b(price|estimate|pricing|worth|value|calculate|cost|profit|show|options|option)\b',
            'stop_loss': r'\b(stop[-\s]?loss|sl|stop|support|risk|exit)\b',
            'unusual': r'\b(unusual|activity|flow|whale|volume|institution)\b'
        }
    
    def parse_query(self, query):
        """Parse a natural language query for options trading parameters with enhanced handling"""
        original_query = query
        query = query.lower()
        
        # Extract ticker - enhanced to avoid common words and check prefixes
        ticker_matches = re.findall(self.ticker_pattern, original_query)
        ticker = None
        for match in ticker_matches:
            if match not in self.common_words:
                ticker = match.upper()
                break
                
        # If we couldn't find a ticker that way, try to find tickers after specific words
        if not ticker:
            # Look for tickers after common prepositions
            for prefix in ['FOR', 'MY', 'WITH', 'ON', 'IN']:
                ticker_after_word = re.search(f'{prefix}\\s+([A-Z]{{1,5}})\\b', original_query)
                if ticker_after_word and ticker_after_word.group(1) not in self.common_words:
                    ticker = ticker_after_word.group(1).upper()
                    break
        
        # Extract strike price with improved handling
        strike_match = re.search(self.strike_pattern, query)
        strike = None
        if strike_match:
            strike_str = strike_match.group(1) or strike_match.group(2)
            # Clean up dollar signs if present
            if strike_str and "$" in strike_str:
                strike_str = strike_str.replace("$", "")
            strike = float(strike_str) if strike_str else None
        
        # Extract expiration date with improved date format handling
        expiry_match = re.search(self.expiry_pattern, query)
        expiry = expiry_match.group(0) if expiry_match else None
        
        # Extract option type (call/put)
        option_type_match = re.search(self.option_type_pattern, query)
        option_type = option_type_match.group(1) if option_type_match else None
        
        # Extract number of contracts
        contract_match = re.search(self.contract_count_pattern, query)
        contract_count = None
        if contract_match:
            # Use the first non-None group from the contract count pattern
            for group in contract_match.groups():
                if group:
                    contract_count = int(group)
                    break
        
        # Extract target price
        target_match = re.search(self.price_target_pattern, query)
        target_price = None
        if target_match:
            target_price = float(target_match.group(1))
        
        # Determine request type
        request_type = None
        for req_type, pattern in self.request_type_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                request_type = req_type
                break
        
        # Default to price estimate if no request type detected
        if not request_type:
            request_type = 'price'
        
        return {
            'ticker': ticker,
            'strike': strike,
            'expiry': expiry,
            'option_type': option_type,
            'request_type': request_type,
            'contract_count': contract_count,
            'target_price': target_price
        }

class OptionsBot(commands.Bot):
    """Discord bot for options trading analysis"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.nlp = OptionsBotNLP()
        
    async def on_ready(self):
        """Called when the bot is ready"""
        print(f'Logged in as {self.user.name} ({self.user.id})')
        print('------')
        
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
        
        # Check if the bot is mentioned
        if self.user not in message.mentions:
            return
        
        # Check channel whitelist
        if config['channel_whitelist'] and str(message.channel.id) not in config['channel_whitelist']:
            return
        
        # Extract the actual query (remove the mention)
        content = message.content.replace(f'<@{self.user.id}>', '').strip()
        
        # Parse the query
        parsed = self.nlp.parse_query(content)
        
        # Check if we have the minimum required information
        if not parsed['ticker']:
            await message.channel.send("❌ I need at least a ticker symbol. Example: @OptionsWizard What's the unusual options activity for TSLA?")
            return
            
        # For unusual activity, we can work without option type
        if parsed['request_type'] == 'unusual' and not parsed['option_type']:
            # Default to both 'call' and 'put'
            parsed['option_type'] = 'both'
        # For other request types, option type is required
        elif not parsed['option_type']:
            await message.channel.send("❌ I need a ticker symbol and option type (call/put). Example: @OptionsWizard What's a good stop loss for AAPL 180 calls expiring next month?")
            return
        
        # Handle the request based on the type
        try:
            if parsed['request_type'] == 'price':
                await self.handle_price_request(message, parsed)
            elif parsed['request_type'] == 'stop_loss':
                await self.handle_stop_loss_request(message, parsed)
            elif parsed['request_type'] == 'unusual':
                await self.handle_unusual_activity_request(message, parsed)
            else:
                await message.channel.send("❓ I'm not sure what you're asking for. I can help with option pricing, stop-loss recommendations, and unusual options activity.")
        except Exception as e:
            await message.channel.send(f"❌ An error occurred: {str(e)}")
            
    async def handle_price_request(self, message, parsed):
        """Handle option price estimation requests"""
        # Call option calculator module
        result = option_calculator.calculate_option_price(
            ticker=parsed['ticker'],
            strike=parsed['strike'],
            expiry=parsed['expiry'],
            option_type=parsed['option_type']
        )
        
        # Format response as Discord embed
        color = discord.Color.green() if parsed['option_type'] == 'call' else discord.Color.red()
        embed = discord.Embed(
            title=f"{parsed['ticker']} {parsed['strike']} {parsed['expiry']} {parsed['option_type'].upper()}",
            color=color
        )
        embed.add_field(name="Option Price", value=f"${result['price']:.2f}", inline=False)
        embed.add_field(name="Greeks", value=f"Delta: {result['delta']:.3f}\nGamma: {result['gamma']:.5f}\nTheta: {result['theta']:.5f}\nVega: {result['vega']:.5f}", inline=False)
        
        # Add theta decay projection
        if 'theta_decay' in result:
            embed.add_field(name="Theta Decay Projection", value=result['theta_decay'], inline=False)
            
        await message.channel.send(embed=embed)
        
    async def handle_stop_loss_request(self, message, parsed):
        """Handle stop-loss recommendation requests"""
        # Call technical analysis module
        result = technical_analysis.calculate_stop_loss(
            ticker=parsed['ticker'],
            strike=parsed['strike'],
            expiry=parsed['expiry'],
            option_type=parsed['option_type']
        )
        
        # Format response as Discord embed
        color = discord.Color.green() if parsed['option_type'] == 'call' else discord.Color.red()
        embed = discord.Embed(
            title=f"{parsed['ticker']} {parsed['strike']} {parsed['expiry']} {parsed['option_type'].upper()}",
            color=color
        )
        embed.add_field(name="Current Option Price", value=f"${result['current_price']:.2f}", inline=False)
        embed.add_field(name="🛑 Recommended Stop-Loss", value=f"${result['stop_loss_price']:.2f} ({result['stop_loss_percentage']:.2f}% from current)", inline=False)
        embed.add_field(name="Trade Horizon", value=result['trade_horizon'], inline=False)
        
        if 'risk_warning' in result:
            embed.add_field(name="⚠️ Risk Warning", value=result['risk_warning'], inline=False)
            
        await message.channel.send(embed=embed)
        
    async def handle_unusual_activity_request(self, message, parsed):
        """Handle unusual options activity requests"""
        # If option_type is 'both', use the combined function
        if parsed['option_type'] == 'both':
            await self.handle_unusual_activity_for_both(message, parsed)
            return
            
        # Get the simplified unusual activity summary
        response_text = unusual_activity.get_simplified_unusual_activity_summary(parsed['ticker'])
        
        # Extract sentiment from the response text to set color
        is_bullish = "bullish" in response_text.lower()
        is_bearish = "bearish" in response_text.lower()
        is_neutral = "neutral" in response_text.lower()
        
        # Set embed color based on sentiment
        if is_bullish and not is_bearish:
            embed_color = discord.Color.green()  # Green for bullish
        elif is_bearish and not is_bullish:
            embed_color = discord.Color.red()  # Red for bearish
        else:
            embed_color = discord.Color.light_gray()  # Grey for neutral or mixed
        
        # Format response as Discord embed with whale emoji
        embed = discord.Embed(
            title=f"🐳 {parsed['ticker']} Unusual Options Activity 🐳",
            color=embed_color
        )
        
        # Use the formatted text directly from the summary (but skip the header since it's in the title)
        if "📊" in response_text:
            # Remove the header line (assumes header ends with first double newline)
            header_end = response_text.find("\n\n")
            if header_end != -1:
                description = response_text[header_end+2:]
            else:
                description = response_text
        else:
            description = response_text
            
        embed.description = description
            
        await message.channel.send(embed=embed)
        
    async def handle_unusual_activity_for_both(self, message, parsed):
        """Handle unusual options activity requests for both calls and puts"""
        # Get the simplified unusual activity summary - the same function works for "both"
        response_text = unusual_activity.get_simplified_unusual_activity_summary(parsed['ticker'])
        
        # Extract sentiment from the response text to set color
        is_bullish = "bullish" in response_text.lower()
        is_bearish = "bearish" in response_text.lower()
        is_neutral = "neutral" in response_text.lower()
        
        # Set embed color based on sentiment
        if is_bullish and not is_bearish:
            embed_color = discord.Color.green()  # Green for bullish
        elif is_bearish and not is_bullish:
            embed_color = discord.Color.red()  # Red for bearish
        else:
            embed_color = discord.Color.light_gray()  # Grey for neutral or mixed
        
        # Format response as Discord embed with whale emoji
        embed = discord.Embed(
            title=f"🐳 {parsed['ticker']} Unusual Options Activity 🐳",
            color=embed_color
        )
        
        # Use the formatted text directly from the summary (but skip the header since it's in the title)
        if "📊" in response_text:
            # Remove the header line (assumes header ends with first double newline)
            header_end = response_text.find("\n\n")
            if header_end != -1:
                description = response_text[header_end+2:]
            else:
                description = response_text
        else:
            description = response_text
            
        embed.description = description
            
        await message.channel.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN_2")
    if not token:
        print("Error: Neither DISCORD_TOKEN nor DISCORD_TOKEN_2 environment variable is set.")
        exit(1)
    
    bot = OptionsBot()
    bot.run(token)
