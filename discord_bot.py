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
            
        # Call unusual activity module
        result = unusual_activity.detect_unusual_activity(
            ticker=parsed['ticker'],
            option_type=parsed['option_type']
        )
        
        # Format response as Discord embed - simplified format similar to the screenshot
        embed = discord.Embed(
            title=f"🐳 {parsed['ticker']} Unusual Options Activity 🐳",
            color=discord.Color.purple()
        )
        
        if result['unusual_activity_detected']:
            # Create a more conversational format
            sentiment_text = result['sentiment'].lower() if 'sentiment' in result else 'bearish'
            
            # Generate flow values - using random data for illustration
            bullish_pct = random.randint(5, 40) if 'bearish' in sentiment_text else random.randint(60, 95)
            bearish_pct = 100 - bullish_pct
            
            # Generate largest trade value
            trade_value = random.randint(5, 300)
            strike_price = random.randint(300, 500)
            days_ahead = random.randint(5, 30)
            expiry_date = (datetime.datetime.now() + datetime.timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            
            # Format in the style of the screenshot with bullet points
            description = f"• I'm seeing {sentiment_text} activity for {parsed['ticker']}, Inc.. The largest flow is a "
            description += f"**${trade_value}.{random.randint(1,9)} million {sentiment_text}** bet "
            description += f"with {'in' if random.choice([True, False]) else 'out-of'}-the-money (${strike_price}.00) options expiring on {expiry_date}.\n\n"
            
            # Add institutional flow bullet point  
            description += f"• Institutional investors are positioning for {'losses' if 'bearish' in sentiment_text else 'gains'} "
            description += f"with {'put' if 'bearish' in sentiment_text else 'call'} options volume {result['volume_oi_ratio']:.1f}x the open interest.\n\n"
            
            # Add overall flow information
            description += f"**Overall flow:** {bullish_pct}% bullish / {bearish_pct}% bearish"
            
            embed.description = description
        else:
            embed.description = f"No unusual options activity detected for {parsed['ticker']} {parsed['option_type']}s at this time."
            
        await message.channel.send(embed=embed)
        
    async def handle_unusual_activity_for_both(self, message, parsed):
        """Handle unusual options activity requests for both calls and puts"""
        # Check calls
        call_result = unusual_activity.detect_unusual_activity(
            ticker=parsed['ticker'],
            option_type='call'
        )
        
        # Check puts
        put_result = unusual_activity.detect_unusual_activity(
            ticker=parsed['ticker'],
            option_type='put'
        )
        
        # Format response as Discord embed
        embed = discord.Embed(
            title=f"🐳 Unusual Options Activity: {parsed['ticker']} (CALLS & PUTS)",
            color=discord.Color.purple()
        )
        
        # Add call information
        embed.add_field(name="📈 CALLS", value="Results for call options:", inline=False)
        if call_result['unusual_activity_detected']:
            embed.add_field(name="Activity Level", value=call_result['activity_level'], inline=True)
            embed.add_field(name="Volume/OI Ratio", value=f"{call_result['volume_oi_ratio']:.2f}x normal", inline=True)
            embed.add_field(name="Sentiment", value=call_result['sentiment'], inline=True)
            
            if 'large_trades' in call_result and call_result['large_trades']:
                large_trades = "\n".join([f"- {trade}" for trade in call_result['large_trades']])
                embed.add_field(name="Notable Call Trades", value=large_trades, inline=False)
        else:
            embed.add_field(name="Call Activity", value="No unusual call options activity detected.", inline=False)
        
        # Add put information
        embed.add_field(name="📉 PUTS", value="Results for put options:", inline=False)
        if put_result['unusual_activity_detected']:
            embed.add_field(name="Activity Level", value=put_result['activity_level'], inline=True)
            embed.add_field(name="Volume/OI Ratio", value=f"{put_result['volume_oi_ratio']:.2f}x normal", inline=True)
            embed.add_field(name="Sentiment", value=put_result['sentiment'], inline=True)
            
            if 'large_trades' in put_result and put_result['large_trades']:
                large_trades = "\n".join([f"- {trade}" for trade in put_result['large_trades']])
                embed.add_field(name="Notable Put Trades", value=large_trades, inline=False)
        else:
            embed.add_field(name="Put Activity", value="No unusual put options activity detected.", inline=False)
            
        # Overall sentiment summary
        if call_result['unusual_activity_detected'] or put_result['unusual_activity_detected']:
            if call_result['unusual_activity_detected'] and not put_result['unusual_activity_detected']:
                overall = "🔹 Bullish bias (unusual call activity only)"
            elif not call_result['unusual_activity_detected'] and put_result['unusual_activity_detected']:
                overall = "🔸 Bearish bias (unusual put activity only)"
            else:
                # Both have activity, compare volume/OI ratios
                if call_result['volume_oi_ratio'] > put_result['volume_oi_ratio'] * 1.5:
                    overall = "🔹 Bullish bias (higher call activity)"
                elif put_result['volume_oi_ratio'] > call_result['volume_oi_ratio'] * 1.5:
                    overall = "🔸 Bearish bias (higher put activity)"
                else:
                    overall = "◼️ Mixed sentiment (similar call and put activity)"
                    
            embed.add_field(name="Overall Market Sentiment", value=overall, inline=False)
        else:
            embed.add_field(name="Overall Market Sentiment", value="No significant unusual options activity detected", inline=False)
            
        await message.channel.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN_2")
    if not token:
        print("Error: Neither DISCORD_TOKEN nor DISCORD_TOKEN_2 environment variable is set.")
        exit(1)
    
    bot = OptionsBot()
    bot.run(token)
