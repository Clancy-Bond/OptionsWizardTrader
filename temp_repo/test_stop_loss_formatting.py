"""
Test script to verify the formatting of stop loss responses.
This will simulate a stop loss request and check the formatting of the response.
"""

import asyncio
import discord
import sys
import os
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add the current directory to path to find modules
sys.path.insert(0, os.getcwd())

# Import the discord bot module
import discord_bot
from discord_bot import OptionsBot, OptionsBotNLP

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
        self.channel = MockChannel()
    
    async def reply(self, content=None, embed=None, mention_author=True):
        print(f"Reply: {content}")
        if embed:
            print_embed(embed)
        return None

class MockChannel:
    async def send(self, content=None, embed=None):
        print(f"Channel send: {content}")
        if embed:
            print_embed(embed)
        return None

class MockUser:
    def __init__(self):
        self.id = 123456789
        self.name = "Test User"
        self.display_name = "Test User"
        self.bot = False

def print_embed(embed):
    """Print the contents of a Discord embed for testing"""
    print("\n" + "="*50)
    print(f"Embed Title: {embed.title}")
    print(f"Description: {embed.description}")
    print(f"Color: {embed.color}")
    print("-"*50)
    
    for field in embed.fields:
        print(f"Field: {field.name}")
        print(f"Value: {field.value}")
        print(f"Inline: {field.inline}")
        print("-"*30)
    
    if hasattr(embed, 'footer') and embed.footer:
        print(f"Footer: {embed.footer.text}")
    print("="*50 + "\n")

async def test_formatting():
    """Test the formatting of stop loss responses"""
    print("Testing stop loss response formatting...")
    
    # Create instances
    nlp_processor = OptionsBotNLP()
    bot = OptionsBot()
    
    # Test queries with different trade horizons
    test_queries = [
        # Long-term (blue)
        "What is the stop loss for AAPL $200 calls for January 2026?",
        # Swing (green)
        "Give me a stop loss for TSLA $250 puts expiring next week",
        # Scalp (orange)
        "Stop loss for SPY $500 calls expiring tomorrow"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        
        # Create a mock message
        message = MockMessage(query)
        
        # Parse the query
        info = nlp_processor.parse_query(query)
        print(f"Parsed info: {info}")
        
        # Process the message
        if info and info.get('request_type') == 'stop_loss':
            await bot.handle_stop_loss_request(message, info)
        else:
            print(f"Query not recognized as stop loss request: {info}")

async def main():
    """Run the test"""
    await test_formatting()

if __name__ == "__main__":
    # Replace Discord's yfinance import
    import yfinance as yf
    
    class MockStock:
        def __init__(self, symbol):
            self.symbol = symbol
            self.history_data = pd.DataFrame({
                'Open': [160.0],
                'High': [165.0],
                'Low': [159.0],
                'Close': [162.50],
                'Volume': [50000000]
            })
            self.options_data = ['2025-04-11', '2025-04-18', '2025-05-16', '2026-01-16']
        
        def history(self, period=None):
            return self.history_data
        
        @property
        def options(self):
            return self.options_data
            
        def option_chain(self, date):
            # Create mock option chain with minimal data needed
            calls = pd.DataFrame({
                'strike': [150, 160, 170, 180, 190, 200],
                'lastPrice': [15.5, 9.8, 5.6, 3.2, 1.8, 0.9],
                'impliedVolatility': [0.25, 0.28, 0.32, 0.35, 0.38, 0.42],
                'volume': [1500, 2500, 3500, 1800, 900, 450],
                'openInterest': [2500, 4500, 6000, 3000, 1500, 800],
                'delta': [0.85, 0.65, 0.45, 0.30, 0.18, 0.09],
                'gamma': [0.04, 0.06, 0.07, 0.05, 0.03, 0.02],
                'theta': [-0.06, -0.08, -0.09, -0.07, -0.05, -0.03],
                'vega': [0.15, 0.25, 0.28, 0.22, 0.18, 0.12]
            })
            
            puts = pd.DataFrame({
                'strike': [150, 160, 170, 180, 190, 200],
                'lastPrice': [0.8, 1.9, 4.2, 8.1, 15.2, 22.1],
                'impliedVolatility': [0.28, 0.30, 0.33, 0.37, 0.40, 0.45],
                'volume': [900, 1500, 2800, 3500, 1900, 1000],
                'openInterest': [1500, 2800, 4500, 6500, 3500, 1800],
                'delta': [-0.15, -0.35, -0.55, -0.70, -0.82, -0.91],
                'gamma': [0.03, 0.05, 0.07, 0.06, 0.04, 0.02],
                'theta': [-0.05, -0.07, -0.10, -0.08, -0.06, -0.04],
                'vega': [0.12, 0.20, 0.27, 0.24, 0.19, 0.15]
            })
            
            class OptionChain:
                def __init__(self, calls_df, puts_df):
                    self.calls = calls_df
                    self.puts = puts_df
            
            return OptionChain(calls, puts)
    
    # Mock yfinance Ticker class to return our mock stock
    yf.Ticker = lambda symbol: MockStock(symbol)
    
    # Run the test
    asyncio.run(main())