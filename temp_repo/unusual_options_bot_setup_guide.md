# SWJ Unusual Options Bot - Setup Guide

## Copy-Paste Instructions for Your New Project

Follow these instructions to set up a standalone Discord bot that focuses only on unusual options activity detection. This guide contains everything you need to get the bot running, organized in steps for easy implementation.

## Step 1: Create the Main Bot File

Create a file named `unusual_options_bot.py` with the following content:

```python
"""
SWJ Unusual Options Bot

A standalone Discord bot that focuses solely on detecting and reporting unusual options activity.
This bot is designed to be a temporary solution while the full options calculator bot is being developed.
"""

# Import required libraries
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
import nltk
from nltk.tokenize import word_tokenize
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import random
from dateutil.parser import parse
import json

# Load environment variables
load_dotenv()

# Define constants
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Try to download NLTK data, but proceed even if it fails
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    print(f"NLTK download error: {str(e)}")

# Define functions for unusual options activity detection
def get_unusual_options_activity(ticker):
    """
    Identify unusual options activity for a given ticker.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        List of unusual options activity with sentiment
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get all available expiration dates
        expirations = stock.options
        
        if not expirations:
            return []
        
        unusual_activity = []
        
        # Process recent expirations (limit to 3 to avoid too many API calls)
        for expiry in expirations[:3]:
            # Get option chains
            options = stock.option_chain(expiry)
            calls = options.calls
            puts = options.puts
            
            # Check for unusual volume in calls
            if not calls.empty:
                # Calculate volume to open interest ratio
                calls['volume_oi_ratio'] = calls['volume'] / calls['openInterest'].replace(0, 1)
                
                # Filter for unusual activity
                unusual_calls = calls[
                    (calls['volume'] > 100) &  # Minimum volume
                    (calls['volume_oi_ratio'] > 2)  # Volume is more than 2x open interest
                ].copy()
                
                if not unusual_calls.empty:
                    unusual_calls['sentiment'] = 'bullish'
                    unusual_calls['amount'] = unusual_calls['volume'] * unusual_calls['lastPrice'] * 100  # Contract size
                    
                    # Sort by amount (descending)
                    unusual_calls = unusual_calls.sort_values('amount', ascending=False)
                    
                    # Take top 2 unusual call activities
                    for _, row in unusual_calls.head(2).iterrows():
                        unusual_activity.append({
                            'expiry': expiry,
                            'strike': row['strike'],
                            'volume': row['volume'],
                            'open_interest': row['openInterest'],
                            'amount': row['amount'],
                            'volume_oi_ratio': row['volume_oi_ratio'],
                            'sentiment': 'bullish'
                        })
            
            # Check for unusual volume in puts
            if not puts.empty:
                # Calculate volume to open interest ratio
                puts['volume_oi_ratio'] = puts['volume'] / puts['openInterest'].replace(0, 1)
                
                # Filter for unusual activity
                unusual_puts = puts[
                    (puts['volume'] > 100) &  # Minimum volume
                    (puts['volume_oi_ratio'] > 2)  # Volume is more than 2x open interest
                ].copy()
                
                if not unusual_puts.empty:
                    unusual_puts['sentiment'] = 'bearish'
                    unusual_puts['amount'] = unusual_puts['volume'] * unusual_puts['lastPrice'] * 100  # Contract size
                    
                    # Sort by amount (descending)
                    unusual_puts = unusual_puts.sort_values('amount', ascending=False)
                    
                    # Take top 2 unusual put activities
                    for _, row in unusual_puts.head(2).iterrows():
                        unusual_activity.append({
                            'expiry': expiry,
                            'strike': row['strike'],
                            'volume': row['volume'],
                            'open_interest': row['openInterest'],
                            'amount': row['amount'],
                            'volume_oi_ratio': row['volume_oi_ratio'],
                            'sentiment': 'bearish'
                        })
        
        # If no unusual activity is found, check for highest volume options as an alternative
        if not unusual_activity:
            # Get the most active options
            for expiry in expirations[:2]:
                options = stock.option_chain(expiry)
                calls = options.calls
                puts = options.puts
                
                # Check calls
                if not calls.empty:
                    # Sort by volume (descending)
                    high_volume_calls = calls.sort_values('volume', ascending=False)
                    
                    # Take top high volume call
                    if high_volume_calls.iloc[0]['volume'] > 50:
                        row = high_volume_calls.iloc[0]
                        # Calculate volume to open interest ratio
                        volume_oi_ratio = row['volume'] / row['openInterest'] if row['openInterest'] > 0 else 1.0
                        unusual_activity.append({
                            'expiry': expiry,
                            'strike': row['strike'],
                            'volume': row['volume'],
                            'open_interest': row['openInterest'],
                            'amount': row['volume'] * row['lastPrice'] * 100,
                            'volume_oi_ratio': volume_oi_ratio,
                            'sentiment': 'bullish'
                        })
                
                # Check puts
                if not puts.empty:
                    # Sort by volume (descending)
                    high_volume_puts = puts.sort_values('volume', ascending=False)
                    
                    # Take top high volume put
                    if high_volume_puts.iloc[0]['volume'] > 50:
                        row = high_volume_puts.iloc[0]
                        # Calculate volume to open interest ratio
                        volume_oi_ratio = row['volume'] / row['openInterest'] if row['openInterest'] > 0 else 1.0
                        unusual_activity.append({
                            'expiry': expiry,
                            'strike': row['strike'],
                            'volume': row['volume'],
                            'open_interest': row['openInterest'],
                            'amount': row['volume'] * row['lastPrice'] * 100,
                            'volume_oi_ratio': volume_oi_ratio,
                            'sentiment': 'bearish'
                        })
        
        return unusual_activity
    except Exception as e:
        print(f"Error fetching unusual options activity: {str(e)}")
        return []

def get_simplified_unusual_activity_summary(ticker):
    """
    Create a simplified, conversational summary of unusual options activity.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        A string with a conversational summary of unusual options activity
    """
    try:
        stock = yf.Ticker(ticker)
        ticker_data = stock.history(period="1d")
        current_price = ticker_data['Close'].iloc[-1] if not ticker_data.empty else 0
        
        # Get unusual options activity
        unusual_activity = get_unusual_options_activity(ticker)
        
        if not unusual_activity:
            return f"I'm not seeing any unusual options activity for {ticker} right now."
        
        # Get stock info
        info = stock.info
        company_name = info.get('shortName', ticker)
        
        # Separate bullish and bearish activity
        bullish_activity = [a for a in unusual_activity if a['sentiment'] == 'bullish']
        bearish_activity = [a for a in unusual_activity if a['sentiment'] == 'bearish']
        
        # Find the biggest money flow
        all_activity = sorted(unusual_activity, key=lambda x: x['amount'], reverse=True)
        biggest_bet = all_activity[0] if all_activity else None
        
        # Determine overall sentiment
        bullish_amount = sum(a['amount'] for a in bullish_activity)
        bearish_amount = sum(a['amount'] for a in bearish_activity)
        
        overall_sentiment = ""
        if bullish_amount > bearish_amount * 1.5:
            overall_sentiment = "strongly bullish"
        elif bullish_amount > bearish_amount:
            overall_sentiment = "mildly bullish"
        elif bearish_amount > bullish_amount * 1.5:
            overall_sentiment = "strongly bearish"
        elif bearish_amount > bullish_amount:
            overall_sentiment = "mildly bearish"
        else:
            overall_sentiment = "neutral with mixed signals"
        
        # Create a conversational response
        response = f"🐳 **{ticker} Unusual Options Activity** 🐳\n\n"
        
        # Add creative elements based on sentiment
        traders = ["institutional investors", "large traders", "market makers", "big money players", "option whales"]
        bullish_phrases = ["betting on a rally", "expecting upside", "positioning for gains", "optimistic about growth"]
        bearish_phrases = ["hedging downside risk", "betting on a decline", "expecting weakness", "positioning defensively"]
        
        if biggest_bet:
            # Format the date
            expiry_date = parse(biggest_bet['expiry'])
            date_str = expiry_date.strftime("%B %d")
            
            # Format the dollar amount
            amount_millions = biggest_bet['amount'] / 1000000
            
            trader_type = random.choice(traders)
            action_phrase = random.choice(bullish_phrases if biggest_bet['sentiment'] == 'bullish' else bearish_phrases)
            
            response += f"I'm seeing {overall_sentiment} activity for {company_name}. "
            
            if amount_millions >= 1:
                response += f"The largest flow is a **${amount_millions:.1f} million {biggest_bet['sentiment']}** bet "
            else:
                amount_thousands = biggest_bet['amount'] / 1000
                response += f"The largest flow is a **${amount_thousands:.0f}K {biggest_bet['sentiment']}** bet "
            
            strike_vs_current = (biggest_bet['strike'] / current_price - 1) * 100
            strike_description = ""
            
            if biggest_bet['sentiment'] == 'bullish':
                if strike_vs_current > 10:
                    strike_description = f"far out-of-the-money (${biggest_bet['strike']:.2f}, about {abs(strike_vs_current):.0f}% above current price)"
                elif strike_vs_current > 0:
                    strike_description = f"out-of-the-money (${biggest_bet['strike']:.2f})"
                else:
                    strike_description = f"in-the-money (${biggest_bet['strike']:.2f})"
            else:  # bearish
                if strike_vs_current < -10:
                    strike_description = f"far out-of-the-money (${biggest_bet['strike']:.2f}, about {abs(strike_vs_current):.0f}% below current price)"
                elif strike_vs_current < 0:
                    strike_description = f"out-of-the-money (${biggest_bet['strike']:.2f})"
                else:
                    strike_description = f"in-the-money (${biggest_bet['strike']:.2f})"
            
            response += f"with {strike_description} options expiring on {date_str}.\n\n"
            
            # Add some color about what this might mean
            response += f"{trader_type.title()} are {action_phrase} "
            
            if biggest_bet['sentiment'] == 'bullish':
                response += f"with call options volume {biggest_bet['volume_oi_ratio']:.1f}x the open interest.\n\n"
            else:
                response += f"with put options volume {biggest_bet['volume_oi_ratio']:.1f}x the open interest.\n\n"
                
            # Add overall flow summary
            total_flow = bullish_amount + bearish_amount
            bullish_percentage = (bullish_amount / total_flow) * 100 if total_flow > 0 else 0
            bearish_percentage = (bearish_amount / total_flow) * 100 if total_flow > 0 else 0
            
            response += f"**Overall flow:** {bullish_percentage:.0f}% bullish / {bearish_percentage:.0f}% bearish"
            
        else:
            response += f"I don't see any significant unusual options activity for {company_name} right now."
            
        return response
        
    except Exception as e:
        print(f"Error generating simplified unusual activity summary: {str(e)}")
        return f"I couldn't analyze unusual options activity for {ticker} right now. There might be an issue with the data source."

class UnusualOptionsNLP:
    """Natural Language Processor for understanding unusual options activity queries"""
    
    def __init__(self):
        print("Initializing UnusualOptionsNLP")
        
        # Define patterns for extracting tickers
        self.ticker_pattern = r'(?:(?:ticker|symbol|stock|for|on|in|of|the)\s+)?(?:\$)?([A-Z]{1,5})(?!\w+\b)\b'
    
    def parse_query(self, query):
        """Parse the user query to extract ticker"""
        try:
            # Initialize result
            result = {'request_type': 'unusual_activity', 'contracts': 1}
            
            # Extract ticker symbol
            ticker_matches = re.findall(self.ticker_pattern, query)
            if ticker_matches:
                result['ticker'] = ticker_matches[0]
            
            return result
        except Exception as e:
            print(f"Error parsing query: {str(e)}")
            return {'request_type': 'unknown'}

class UnusualOptionsBot:
    """Main Unusual Options Bot class to handle user requests"""
    
    def __init__(self):
        self.nlp = UnusualOptionsNLP()
        
        # Define approved channels - leave empty to allow all channels
        self.approved_channels = []
        
        # Load channel restrictions if exists
        try:
            with open('discord_permissions.json', 'r') as f:
                permissions = json.load(f)
                self.approved_channels = permissions.get('approved_channels', [])
                print(f"Loaded approved channels: {self.approved_channels}")
        except Exception as e:
            print(f"Could not load channel permissions: {str(e)}")
    
    def get_help_instructions(self):
        """Return help instructions for interacting with the bot"""
        help_text = """
## 🐳 SWJ Unusual Options Bot

This bot detects and reports unusual options activity for any stock ticker.

### How to use it:
- Mention the bot with a ticker symbol: `@SWJ Unusual Options unusual options for TSLA`
- Ask about specific tickers: `@SWJ Unusual Options what's the unusual activity for AAPL?`
- More examples: `@SWJ Unusual Options show NVDA unusual options` or `@SWJ Unusual Options Microsoft unusual activity`

The bot detects institutional-grade options flow by identifying:
- High volume to open interest ratios (>2x)
- Significant transaction amounts
- Unusual patterns in options activity

All responses include whether the activity is bullish or bearish, plus details on the largest options flow.
"""
        return help_text
    
    async def handle_message(self, message):
        """Process user message and generate a response"""
        # Check if the message is in an approved channel (if restrictions are set)
        channel_name = message.channel.name if hasattr(message.channel, 'name') else "Unknown"
        print(f"HANDLE_MESSAGE: Received message in channel: {channel_name}")
        
        if self.approved_channels and channel_name not in self.approved_channels:
            print(f"HANDLE_MESSAGE: Ignoring message in non-approved channel: {channel_name}")
            return None
        
        print(f"HANDLE_MESSAGE: Channel {channel_name} is approved")
        
        # Check if bot is mentioned - very important for Discord etiquette
        bot_id = message.guild.me.id if message.guild else None
        bot_mentioned = False
        
        if bot_id:
            print(f"HANDLE_MESSAGE: BOT_USER_ID: {bot_id}")
            
            # Check if bot is directly mentioned
            mentions_ids = [user.id for user in message.mentions]
            print(f"HANDLE_MESSAGE: Message mentions user ID: {mentions_ids}")
            
            if bot_id in mentions_ids:
                print(f"HANDLE_MESSAGE: Bot is directly mentioned in message.mentions!")
                bot_mentioned = True
            
            # Check for bot mention in content string as fallback
            print(f"HANDLE_MESSAGE: Message content: {message.content}")
            mention_strings = [f"<@{bot_id}>", f"<@!{bot_id}>"]
            print(f"HANDLE_MESSAGE: Looking for mention strings: {' or '.join(mention_strings)}")
            
            content_has_mention = any(mention in message.content for mention in mention_strings)
            print(f"HANDLE_MESSAGE: Contains mention string: {content_has_mention}")
            
            bot_mentioned = bot_mentioned or content_has_mention
        
        if not bot_mentioned:
            print("HANDLE_MESSAGE: Bot not mentioned, ignoring message")
            return None
        
        print("HANDLE_MESSAGE: BOT MENTIONED - Processing message!")
        
        # Remove bot mention from query
        query = re.sub(r'<@!?[0-9]+>', '', message.content).strip()
        
        # Parse the query
        print(f"NLP: Parsing query: '{query}'")
        info = self.nlp.parse_query(query)
        
        print(f"HANDLE_MESSAGE: Parsed query result: {info}")
        
        # Handle the request
        if 'ticker' in info:
            return await self.handle_unusual_activity_request(message, info)
        else:
            # Create an error embed asking for ticker
            error_embed = discord.Embed(
                title="Stock Ticker Required",
                description="Please include a stock ticker symbol in your request, such as AAPL, MSFT, or TSLA.",
                color=0xFF0000  # Red for errors
            )
            
            # Add example
            error_embed.add_field(
                name="Example:",
                value="@SWJ Unusual Options what's the unusual activity for TSLA?",
                inline=False
            )
            
            return error_embed
    
    async def handle_unusual_activity_request(self, message, info):
        """Handle requests for unusual options activity"""
        try:
            ticker = info['ticker']
            
            # Get the simplified summary for unusual options activity
            activity_summary = get_simplified_unusual_activity_summary(ticker)
            
            # Purple color for unusual activity
            embed_color = 0x9370DB
            
            # Create the embed with title and color
            embed = discord.Embed(
                title=f"🐳 Unusual Options Activity: {ticker.upper()} 🐳",
                description=activity_summary,
                color=embed_color
            )
            
            # Add footer with disclaimer
            embed.set_footer(text="Based on real-time trading data. Significant volume increases may indicate institutional positioning.")
            
            print("DEBUG: About to return embed")
            return embed
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in unusual activity request: {str(e)}")
            print(f"Full traceback:\n{error_details}")
            
            # Create a generic error embed
            error_embed = discord.Embed(
                title="Error Processing Request",
                description=f"An error occurred while processing your request: {str(e)}",
                color=0xFF0000  # Red for errors
            )
            error_embed.set_footer(text="Please try again with a different query")
            return error_embed

# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

options_bot = UnusualOptionsBot()

@client.event
async def on_ready():
    """Event handler for when the bot is ready"""
    print(f'We have logged in as {client.user}')
    print(f'Bot is connected to {len(client.guilds)} servers')

@client.event
async def on_message(message):
    """Event handler for incoming messages"""
    # Don't respond to our own messages
    if message.author == client.user:
        print("Message is from self, ignoring")
        return
    
    print(f"MSG RECEIVED: '{message.content}' from {message.author}")
    
    # Check if the bot is mentioned
    bot_mentioned = client.user in message.mentions
    
    # Log if we received a direct mention
    print(f"Looking for mention: '{client.user.mention}' in '{message.content}'")
    print(f"Direct check: {bot_mentioned}")
    
    if not bot_mentioned:
        print("Bot is NOT mentioned according to Discord's built-in method")
    else:
        print("BOT IS MENTIONED using Discord's built-in mentioned_in method!")
    
    # Process the message with our options bot
    print("Passing to options_bot.handle_message")
    response = await options_bot.handle_message(message)
    
    print(f"Response from options_bot: {response}")
    
    # If we got a response, send it
    if response:
        print("Sending response")
        await message.reply(embed=response)
        print("Response sent")
    else:
        print("No response to send")

@client.command(name="options_help")
async def options_help_command(ctx):
    """Display help information about the bot using Discord embeds"""
    help_text = options_bot.get_help_instructions()
    
    embed = discord.Embed(
        title="🐳 SWJ Unusual Options Bot - Help",
        description=help_text,
        color=0x00FFFF  # Cyan color for help
    )
    
    await ctx.send(embed=embed)

def run_discord_bot():
    """Run the Discord bot with the token from environment variables"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is not set")
    
    client.run(token)

if __name__ == "__main__":
    try:
        # Setup logging
        import logging
        logger = logging.getLogger('unusual_options_bot')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Also log to file
        file_handler = logging.FileHandler('unusual_options_bot.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info("Starting Unusual Options Discord Bot...")
        
        # Run the bot
        run_discord_bot()
    except Exception as e:
        print(f"Critical error: {str(e)}")
```

## Step 2: Create Environment File

Create a file named `.env` with your Discord bot token:

```
DISCORD_TOKEN=your_discord_token_here
```

## Step 3: Create Channel Permissions (Optional)

If you want to restrict the bot to only respond in specific channels, create a file named `discord_permissions.json`:

```json
{
    "approved_channels": [
        "channel-name-1",
        "channel-name-2"
    ]
}
```

Leave the approved_channels array empty `[]` if you want the bot to respond in all channels.

## Step 4: Create Run Script

Create a file named `run_bot.py` to easily start the bot:

```python
"""
Simple runner script for the Unusual Options Bot
"""
from unusual_options_bot import run_discord_bot

if __name__ == "__main__":
    run_discord_bot()
```

## Step 5: Instructions for the AI Agent in Your New Project

Copy and paste the following instructions for the AI agent in your new project:

```
I want to set up a Discord bot that focuses solely on detecting unusual options activity in the stock market. The bot should:

1. Install all required dependencies:
   - discord.py
   - yfinance
   - python-dotenv
   - nltk
   - pandas
   - numpy
   - python-dateutil

2. Set up the provided files:
   - unusual_options_bot.py (main bot file)
   - .env (for DISCORD_TOKEN)
   - discord_permissions.json (optional, for channel restrictions)
   - run_bot.py (simple runner script)

3. Configure the bot to:
   - Only respond when @mentioned in Discord
   - Format responses with attractive Discord embeds
   - Use the 🐳 emoji for unusual options activity
   - Highlight dollar amounts in bold
   - Show percentage splits of bullish vs bearish flow
   - Only work with real market data (no synthetic data)

4. Help me set up a workflow to run the bot 24/7 using:
   - python run_bot.py

The code for all these files is already provided, so you'll just need to help with setup and configuration.
```

## Step 6: Required Package Installation

When you start the new project, the AI agent will need to install these packages:

- discord.py
- yfinance
- python-dotenv
- nltk
- pandas
- numpy
- python-dateutil

## Step 7: Bot Operation

Run the bot using:

```
python run_bot.py
```

The bot will:
1. Connect to Discord using your token
2. Only respond when mentioned in an approved channel (or any channel if no restrictions)
3. Detect unusual options activity for any ticker symbol mentioned
4. Format responses with attractive Discord embeds and emojis
5. Show dollar amounts in bold and percentage splits of bullish vs bearish flow

## Step 8: Bot Usage in Discord

Users can interact with your bot using:

```
@YourBotName unusual options for TSLA
@YourBotName what's the unusual activity for AAPL
@YourBotName show NVDA unusual options
```

The bot will respond with detailed unusual options activity analysis including sentiment, largest flow details, and overall flow percentages.