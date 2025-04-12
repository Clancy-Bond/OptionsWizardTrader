"""
Test script for unusual options activity through the Discord bot interface
"""

import discord_bot
from discord_bot import OptionsBotNLP
import asyncio

async def test_unusual_activity(ticker):
    """
    Test unusual options activity detection through the Discord bot interface
    """
    print(f"\n=== TESTING UNUSUAL OPTIONS ACTIVITY FOR {ticker} ===\n")
    
    # Create the bot and NLP processor
    bot = discord_bot.OptionsBot()
    nlp = OptionsBotNLP()
    
    # Parse the query
    query = f"check unusual options activity for {ticker}"
    parsed = nlp.parse_query(query)
    print(f"Parsed query: {parsed}")
    
    # Create a mock message
    class MockMessage:
        content = query
        author = type('obj', (object,), {'id': 123456})
        channel = type('obj', (object,), {'id': 789012})
        
        async def reply(self, content):
            print(f"Bot response: {content}")
    
    # Handle the request
    await bot.handle_unusual_activity_request(MockMessage(), parsed)

if __name__ == "__main__":
    ticker = input("Enter ticker to test (e.g., AAPL): ").strip().upper()
    asyncio.run(test_unusual_activity(ticker))