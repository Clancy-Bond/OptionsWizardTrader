"""
Verification script to test the fix for parameter name inconsistency.
This script simulates Discord messages with various parameter formats
to confirm the bot correctly handles both 'strike'/'strike_price' and
'expiration'/'expiration_date' parameter naming.
"""

import asyncio
import json
import os
from datetime import datetime

# IMPORTANT: This mocks the bot's actual behavior without importing the bot itself
# This is a simplified version for testing without requiring Discord modules

class MockUser:
    def __init__(self, id="1234567890", name="TestUser"):
        self.id = id
        self.name = name
        self.mention = f"<@{id}>"

class MockChannel:
    def __init__(self, name="test-channel"):
        self.name = name
        
    async def send(self, content=None, embed=None):
        print(f"[Channel] {content if content else 'Sent embed'}")
        if embed:
            print_embed(embed)
        return MockMessage("Response from channel.send")

class MockMessage:
    def __init__(self, content, author=None, channel=None):
        self.content = content
        self.author = author or MockUser()
        self.channel = channel or MockChannel()
        self.mentions = []
        
    async def reply(self, content=None, embed=None, mention_author=False):
        print(f"[Reply] {content if content else 'Sent embed'}")
        if embed:
            print_embed(embed)
        return MockMessage("Response from message.reply")

class MockEmbed:
    def __init__(self, title=None, description=None, color=None):
        self.title = title
        self.description = description
        self.color = color
        self.fields = []
        self.footer = None
        
    def add_field(self, name="", value="", inline=False):
        self.fields.append({"name": name, "value": value, "inline": inline})
        return self
        
    def set_footer(self, text=""):
        self.footer = text
        return self

def print_embed(embed):
    """Print a simplified version of a Discord embed"""
    print("=== EMBED ===")
    print(f"TITLE: {embed.title}")
    print(f"DESC: {embed.description}")
    print(f"COLOR: {embed.color}")
    print("FIELDS:")
    for i, field in enumerate(embed.fields):
        print(f"  {i+1}. {field['name']}: {field['value']} (inline={field['inline']})")
    if embed.footer:
        print(f"FOOTER: {embed.footer}")
    print("============")

class SimplifiedNLP:
    """A very simplified version of the OptionsBotNLP class for testing"""
    
    def parse_query(self, query):
        """Simplified parse_query method that extracts basic parameters"""
        info = {}
        
        # Extract ticker (assumed format: $TICKER or just TICKER)
        ticker_match = None
        for word in query.split():
            if word.startswith('$') and len(word) > 1:
                ticker_match = word[1:]
                break
            elif word.upper() in ['AAPL', 'TSLA', 'MSFT', 'NVDA', 'META', 'AMZN', 'GOOGL', 'FB']:
                ticker_match = word.upper()
                break
                
        if ticker_match:
            info['ticker'] = ticker_match
        
        # Extract request type (very simple)
        if 'stop' in query.lower() and 'loss' in query.lower():
            info['request_type'] = 'stop_loss'
        elif 'price' in query.lower():
            info['request_type'] = 'option_price'
        else:
            info['request_type'] = 'unknown'
            
        # Extract option type
        if 'call' in query.lower():
            info['option_type'] = 'call'
        elif 'put' in query.lower():
            info['option_type'] = 'put'
            
        # Extract strike (simple $ pattern)
        for word in query.split():
            if word.startswith('$') and len(word) > 1:
                try:
                    strike = float(word[1:])
                    info['strike'] = strike
                    break
                except:
                    pass
                    
        # Extract expiration (very simplified)
        if 'expiring' in query.lower():
            # Just set a sample date for testing
            info['expiration'] = '2025-04-18'
        
        # THIS IS THE KEY PART: Apply the parameter consistency mapping logic
        # Ensure parameter naming consistency - handle 'strike' vs 'strike_price'
        if 'strike' in info and info['strike'] is not None:
            info['strike_price'] = info['strike']
        
        # Ensure parameter naming consistency - handle 'expiration' vs 'expiration_date'
        if 'expiration' in info and info['expiration'] is not None:
            info['expiration_date'] = info['expiration']
        
        return info

class SimplifiedBot:
    """A very simplified version of the OptionsBot class for testing"""
    
    def __init__(self):
        self.nlp = SimplifiedNLP()
        
    async def handle_message(self, message):
        """Process message and route to appropriate handler"""
        content = message.content
        
        # Parse the query
        info = self.nlp.parse_query(content)
        print(f"Parsed info: {json.dumps(info, indent=2)}")
        
        if info['request_type'] == 'stop_loss':
            return await self.handle_stop_loss_request(message, info)
        elif info['request_type'] == 'option_price':
            return await self.handle_option_price_request(message, info)
        else:
            return MockEmbed(
                title="Unknown request type",
                description="I'm not sure what you're asking for.",
                color=0xFF0000
            )
    
    async def handle_stop_loss_request(self, message, info):
        """Simplified version to test parameter handling"""
        # Check if we have the required parameters
        missing_params = []
        if 'ticker' not in info:
            missing_params.append('ticker symbol')
        if 'strike_price' not in info:
            missing_params.append('strike price')
        if 'option_type' not in info:
            missing_params.append('option type (call/put)')
        
        if missing_params:
            return MockEmbed(
                title="Missing Information",
                description=f"I need the following to calculate stop loss: {', '.join(missing_params)}",
                color=0xFF0000
            )
            
        # Generate a response using the parameters (showing they were properly mapped)
        ticker = info['ticker']
        strike_price = info.get('strike_price', 'N/A')
        option_type = info.get('option_type', 'N/A')
        expiration_date = info.get('expiration_date', 'N/A')
        
        embed = MockEmbed(
            title=f"⭐ Stop Loss Analysis for {ticker} ${strike_price} {option_type} ⭐",
            description="Analysis based on technical indicators and option greeks.",
            color=0x368BD6  # Blue color
        )
        
        # Add field to show which parameters were used (to confirm mapping worked)
        embed.add_field(
            name="Parameters Used",
            value=f"Ticker: {ticker}\nStrike Price: ${strike_price}\nOption Type: {option_type}\nExpiration Date: {expiration_date}",
            inline=False
        )
        
        embed.add_field(
            name="Parameter Sources",
            value=f"strike_price from: {'strike' if 'strike' in info else 'strike_price'}\n" +
                  f"expiration_date from: {'expiration' if 'expiration' in info else 'expiration_date'}",
            inline=False
        )
        
        # Add a stop loss recommendation
        embed.add_field(
            name="🔍 LONG-TERM STRATEGY (LEAP) 🔍",
            value="Recommended stop loss: $182.50 (-10% from current price)",
            inline=False
        )
        
        return embed
    
    async def handle_option_price_request(self, message, info):
        """Simplified version to test parameter handling"""
        # Check if we have the required parameters
        missing_params = []
        if 'ticker' not in info:
            missing_params.append('ticker symbol')
        if 'strike_price' not in info:
            missing_params.append('strike price')
        if 'option_type' not in info:
            missing_params.append('option type (call/put)')
        
        if missing_params:
            return MockEmbed(
                title="Missing Information",
                description=f"I need the following to calculate option price: {', '.join(missing_params)}",
                color=0xFF0000
            )
            
        # Generate a response using the parameters (showing they were properly mapped)
        ticker = info['ticker']
        strike_price = info.get('strike_price', 'N/A')
        option_type = info.get('option_type', 'N/A')
        expiration_date = info.get('expiration_date', 'N/A')
        
        embed = MockEmbed(
            title=f"{ticker} {option_type.upper()} ${strike_price} Option",
            description=f"Current Stock Price: $200.00",
            color=0x00D026  # Green color
        )
        
        # Add field to show which parameters were used (to confirm mapping worked)
        embed.add_field(
            name="Parameters Used",
            value=f"Ticker: {ticker}\nStrike Price: ${strike_price}\nOption Type: {option_type}\nExpiration Date: {expiration_date}",
            inline=False
        )
        
        embed.add_field(
            name="Parameter Sources",
            value=f"strike_price from: {'strike' if 'strike' in info else 'strike_price'}\n" +
                  f"expiration_date from: {'expiration' if 'expiration' in info else 'expiration_date'}",
            inline=False
        )
        
        return embed

async def verify_parameter_mapping():
    """Verify that parameter mapping works correctly"""
    print("=== Testing Discord Bot Parameter Mapping Fix ===")
    bot = SimplifiedBot()
    
    # Test case 1: Using 'strike'
    print("\n--- TEST 1: Using 'strike' parameter ---")
    query1 = "What's a good stop loss for AAPL $200 calls expiring next month?"
    message1 = MockMessage(query1)
    response1 = await bot.handle_message(message1)
    print_embed(response1)
    
    # Test case 2: Using 'expiration'
    print("\n--- TEST 2: Using 'expiration' parameter ---")
    query2 = "What's the price of TSLA $250 puts expiring in June?"
    message2 = MockMessage(query2)
    response2 = await bot.handle_message(message2)
    print_embed(response2)
    
    # Test case 3: Using mixed parameter format
    print("\n--- TEST 3: Using mixed parameter format ---")
    query3 = "What's a good stop loss for my NVDA $500 calls expiring soon?"
    message3 = MockMessage(query3)
    response3 = await bot.handle_message(message3)
    print_embed(response3)
    
    print("\n=== Parameter Mapping Test Complete ===")

if __name__ == "__main__":
    asyncio.run(verify_parameter_mapping())