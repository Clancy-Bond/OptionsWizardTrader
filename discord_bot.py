import os
import re
import discord
import json
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
        # Regex patterns for extracting information from queries
        self.ticker_pattern = r'\b([A-Z]{1,5})\b'
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
        
        # Extract ticker
        ticker_match = re.search(self.ticker_pattern, query, re.IGNORECASE)
        ticker = ticker_match.group(1).upper() if ticker_match else None
        
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
        if not parsed['ticker'] or not parsed['option_type']:
            await message.channel.send("❌ I need at least a ticker symbol and option type (call/put). Example: @OptionsWizard What's a good stop loss for AAPL 180 calls expiring next month?")
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
        # Call unusual activity module
        result = unusual_activity.detect_unusual_activity(
            ticker=parsed['ticker'],
            option_type=parsed['option_type']
        )
        
        # Format response as Discord embed
        embed = discord.Embed(
            title=f"🐳 Unusual Options Activity: {parsed['ticker']} {parsed['option_type'].upper()}S",
            color=discord.Color.purple()
        )
        
        if result['unusual_activity_detected']:
            embed.add_field(name="Activity Level", value=result['activity_level'], inline=False)
            embed.add_field(name="Volume/OI Ratio", value=f"{result['volume_oi_ratio']:.2f}x normal", inline=False)
            embed.add_field(name="Sentiment", value=result['sentiment'], inline=False)
            
            if 'large_trades' in result and result['large_trades']:
                large_trades = "\n".join([f"- {trade}" for trade in result['large_trades']])
                embed.add_field(name="Notable Trades", value=large_trades, inline=False)
        else:
            embed.add_field(name="Result", value="No unusual options activity detected for this ticker/option type.", inline=False)
            
        await message.channel.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN environment variable is not set.")
        exit(1)
    
    bot = OptionsBot()
    bot.run(token)
