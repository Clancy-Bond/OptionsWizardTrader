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
from utils_file import is_valid_ticker, COMMON_WORDS, fetch_all_tickers, VALIDATED_TICKERS

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
        # Regex patterns for extracting information from queries
        # Specialized pattern for extracting tickers, improved to handle any case and context
        # This pattern will find potential tickers anywhere in the text, regardless of capitalization
        self.ticker_pattern = r'(?:(?:ticker|symbol|stock|for|on|in|of|the)\s+)?(?:\$)?([A-Za-z]{1,5})(?!\w+\b)\b|(?:\$)([A-Za-z]{1,5})'
        
        # Using the extensive common words list imported from utils_file
        self.excluded_words = COMMON_WORDS
        print(f"Loaded {len(COMMON_WORDS)} common words for ticker filtering")
        self.strike_pattern = r'\$?(\d+(?:\.\d+)?)'
        self.expiry_pattern = r'(\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?)|(\d{1,2}[- ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[- ]\d{2,4})'
        self.option_type_pattern = r'\b(call|put)s?\b'
        self.request_type_patterns = {
            'price': r'\b(price|estimate|pricing|worth|value)\b',
            'stop_loss': r'\b(stop[-\s]?loss|sl|stop)\b',
            'unusual': r'\b(unusual|activity|flow|whale|institution)\b'
        }
    
    def parse_query(self, query):
        """Parse a natural language query for options trading parameters"""
        query = query.lower()
        
        # Extract ticker using findall to get all matches
        ticker_matches = re.findall(self.ticker_pattern, query, re.IGNORECASE)
        
        # Process matches - our pattern can return tuples if there are multiple capture groups
        processed_matches = []
        for match in ticker_matches:
            if isinstance(match, tuple):
                # Process each group in the tuple that's not empty
                for group in match:
                    if group and len(group) > 0:
                        processed_matches.append(group)
            else:
                processed_matches.append(match)
        
        # Filter out non-tickers and common words
        valid_tickers = []
        for match in processed_matches:
            # Convert to uppercase for consistent comparison
            match_upper = match.upper()
            
            # Skip empty or too short matches
            if not match_upper or len(match_upper) < 1:
                continue
                
            # Skip common words
            if match_upper in self.excluded_words:
                continue
                
            # Check if it's a valid ticker with our validation function
            if is_valid_ticker(match_upper):
                valid_tickers.append(match_upper)
        
        # If we found valid tickers, use the first one
        if valid_tickers:
            ticker = valid_tickers[0]
        # If we have no valid tickers but querying for unusual activity
        elif "unusual" in query.lower() or "activity" in query.lower():
            # No valid ticker was found, but this is an unusual activity request
            ticker = None  # Let the bot show a message asking for a ticker
        # Legacy fallback - first potential ticker that's not excluded
        elif processed_matches:
            potential_ticker = processed_matches[0].upper()
            if potential_ticker not in self.excluded_words:
                ticker = potential_ticker
            else:
                ticker = None
        else:
            ticker = None
        
        # Extract strike price
        strike_match = re.search(self.strike_pattern, query)
        strike = float(strike_match.group(1)) if strike_match else None
        
        # Extract expiration date
        expiry_match = re.search(self.expiry_pattern, query)
        expiry = expiry_match.group(0) if expiry_match else None
        
        # Extract option type (call/put)
        option_type_match = re.search(self.option_type_pattern, query)
        option_type = option_type_match.group(1) if option_type_match else None
        
        # Determine request type
        request_type = None
        for req_type, pattern in self.request_type_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                request_type = req_type
                break
        
        # Special handling for unusual options activity
        if "unusual" in query.lower() or "activity" in query.lower() or "flow" in query.lower():
            request_type = 'unusual'
        
        # Default to price estimate if no request type detected
        if not request_type:
            request_type = 'price'
        
        return {
            'ticker': ticker,
            'strike': strike,
            'expiry': expiry,
            'option_type': option_type,
            'request_type': request_type
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
        
        # Load all ticker symbols for improved recognition
        print("Loading comprehensive ticker list...")
        VALIDATED_TICKERS.update(fetch_all_tickers())
        print(f"Loaded {len(VALIDATED_TICKERS)} total tickers for validation")
        
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
        
        # Determine what type of response we have
        using_fallback = "not available through our data provider" in response_text.lower()
        no_activity = "no significant unusual options activity" in response_text.lower()
        has_whale_emoji = "🐳" in response_text
        
        if using_fallback:
            # Data is limited due to API restrictions
            embed = discord.Embed(
                title=f"📊 {parsed['ticker']} Market Data",
                color=discord.Color.blue()  # Blue for informational
            )
            
            # Process the description
            header_end = response_text.find("\n\n")
            if header_end != -1:
                description = response_text[header_end+2:]
            else:
                description = response_text
                
            embed.description = description
            embed.set_footer(text="Some premium data requires API plan upgrade. Using basic stock data.")
            
        elif no_activity and not has_whale_emoji:
            # No unusual activity detected
            embed = discord.Embed(
                title=f"📊 {parsed['ticker']} No Unusual Activity",
                color=discord.Color.light_gray()  # Grey for neutral
            )
            
            # Process the description
            header_end = response_text.find("\n\n")
            if header_end != -1:
                description = response_text[header_end+2:]
            else:
                description = response_text
                
            embed.description = description
            
        else:
            # Standard unusual activity response with sentiment
            # Check for overall flow percentages to determine color
            import re
            
            # Look for the percentage pattern in overall flow
            flow_pattern = r"Overall flow:\s*(\d+)%\s+bullish\s*[/]\s*(\d+)%\s+bearish"
            flow_match = re.search(flow_pattern, response_text, re.IGNORECASE)
            
            if flow_match:
                # Extract percentages
                bullish_pct = int(flow_match.group(1))
                bearish_pct = int(flow_match.group(2))
                
                # Set color based on which percentage is higher
                if bullish_pct > bearish_pct:
                    embed_color = discord.Color.green()  # Green for majority bullish
                elif bearish_pct > bullish_pct:
                    embed_color = discord.Color.red()  # Red for majority bearish
                else:
                    embed_color = discord.Color.light_gray()  # Grey for 50-50
            else:
                # Fallback to keyword detection if percentages not found
                is_bullish = "bullish" in response_text.lower()
                is_bearish = "bearish" in response_text.lower()
                
                # Set embed color based on sentiment keywords
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
            
            # Process the description
            if has_whale_emoji:
                header_end = response_text.find("\n\n")
                if header_end != -1:
                    description = response_text[header_end+2:]
                else:
                    description = response_text
            else:
                description = response_text
                
            embed.description = description
            
        # Add timestamp to all responses
        from datetime import datetime
        # No timestamp
            
        await message.channel.send(embed=embed)
        
    async def handle_unusual_activity_for_both(self, message, parsed):
        """Handle unusual options activity requests for both calls and puts"""
        # Get the simplified unusual activity summary - the same function works for "both"
        response_text = unusual_activity.get_simplified_unusual_activity_summary(parsed['ticker'])
        
        # Determine what type of response we have
        using_fallback = "not available through our data provider" in response_text.lower()
        no_activity = "no significant unusual options activity" in response_text.lower()
        has_whale_emoji = "🐳" in response_text
        
        if using_fallback:
            # Data is limited due to API restrictions
            embed = discord.Embed(
                title=f"📊 {parsed['ticker']} Market Data",
                color=discord.Color.blue()  # Blue for informational
            )
            
            # Process the description
            header_end = response_text.find("\n\n")
            if header_end != -1:
                description = response_text[header_end+2:]
            else:
                description = response_text
                
            embed.description = description
            embed.set_footer(text="Some premium data requires API plan upgrade. Using basic stock data.")
            
        elif no_activity and not has_whale_emoji:
            # No unusual activity detected
            embed = discord.Embed(
                title=f"📊 {parsed['ticker']} No Unusual Activity",
                color=discord.Color.light_gray()  # Grey for neutral
            )
            
            # Process the description
            header_end = response_text.find("\n\n")
            if header_end != -1:
                description = response_text[header_end+2:]
            else:
                description = response_text
                
            embed.description = description
            
        else:
            # Standard unusual activity response with sentiment
            # Check for overall flow percentages to determine color
            import re
            
            # Look for the percentage pattern in overall flow
            flow_pattern = r"Overall flow:\s*(\d+)%\s+bullish\s*[/]\s*(\d+)%\s+bearish"
            flow_match = re.search(flow_pattern, response_text, re.IGNORECASE)
            
            if flow_match:
                # Extract percentages
                bullish_pct = int(flow_match.group(1))
                bearish_pct = int(flow_match.group(2))
                
                # Set color based on which percentage is higher
                if bullish_pct > bearish_pct:
                    embed_color = discord.Color.green()  # Green for majority bullish
                elif bearish_pct > bullish_pct:
                    embed_color = discord.Color.red()  # Red for majority bearish
                else:
                    embed_color = discord.Color.light_gray()  # Grey for 50-50
            else:
                # Fallback to keyword detection if percentages not found
                is_bullish = "bullish" in response_text.lower()
                is_bearish = "bearish" in response_text.lower()
                
                # Set embed color based on sentiment keywords
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
            
            # Process the description
            if has_whale_emoji:
                header_end = response_text.find("\n\n")
                if header_end != -1:
                    description = response_text[header_end+2:]
                else:
                    description = response_text
            else:
                description = response_text
                
            embed.description = description
            
        # Add timestamp to all responses
        from datetime import datetime
        # No timestamp
            
        await message.channel.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN_2")
    if not token:
        print("Error: Neither DISCORD_TOKEN nor DISCORD_TOKEN_2 environment variable is set.")
        exit(1)
    
    bot = OptionsBot()
    bot.run(token)
