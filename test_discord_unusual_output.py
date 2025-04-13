"""
Test Discord bot's unusual options activity formatter directly
"""

import asyncio
import discord
from discord.ext import commands
from discord_bot import OptionsBot

async def test_discord_unusual():
    # Create a message-like object for testing
    class MockMessage:
        def __init__(self):
            self.content = "!unusual TSLA"
            self.author = MockUser()
            self.channel = MockChannel()
            
        async def reply(self, content=None, embed=None):
            print("\nReply content:")
            print(content)
            if embed:
                print("\nEmbed title:", embed.title)
                print("Embed description:", embed.description)
                
    class MockUser:
        def __init__(self):
            self.id = 12345
            self.name = "TestUser"
            
    class MockChannel:
        def __init__(self):
            self.id = 67890
            self.name = "test-channel"
            
        async def send(self, content=None, embed=None):
            print("\nChannel message:")
            print(content)
            if embed:
                print("\nEmbed title:", embed.title)
                print("Embed description:", embed.description)
    
    # Initialize the bot
    bot = OptionsBot()
    
    # Create parsed result like NLP would produce
    class MockParsed:
        def __init__(self):
            self.ticker = "TSLA"
            self.option_type = None
            self.expiration = None
            self.strike = None
        
    # Call the unusual activity handler directly
    message = MockMessage()
    parsed = MockParsed()
    
    print("\nTesting unusual options activity for TSLA...")
    await bot.handle_unusual_activity_request(message, parsed)
    
    # Try another ticker
    parsed.ticker = "AAPL"
    print("\nTesting unusual options activity for AAPL...")
    await bot.handle_unusual_activity_request(message, parsed)

if __name__ == "__main__":
    asyncio.run(test_discord_unusual())