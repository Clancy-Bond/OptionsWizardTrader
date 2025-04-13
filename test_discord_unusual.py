"""
Test script that simulates the Discord bot's processing of an unusual options activity request
"""
import asyncio
import discord_bot
from discord.ext import commands

async def test_unusual_activity_command():
    """Test the unusual options activity command processing directly"""
    # Create a bot instance but don't connect to Discord
    bot = discord_bot.OptionsBot()
    
    # Create mock classes for Discord objects
    class MockChannel:
        def __init__(self):
            self.id = 789012
            
        async def send(self, content, embed=None):
            print("Channel Message:")
            print("-" * 60)
            print(content)
            if embed:
                print("\nEmbed Title:", embed.title)
                print("Embed Description:", embed.description)
            print("-" * 60)
            return MockMessage("", self)
    
    class MockAuthor:
        def __init__(self):
            self.id = 123456
    
    # Create a mock message class
    class MockMessage:
        def __init__(self, content, channel=None):
            self.content = content
            self.author = MockAuthor()
            self.channel = channel if channel else MockChannel()
            
        async def reply(self, content, embed=None):
            print("Reply Message:")
            print("-" * 60)
            print(content)
            if embed:
                print("\nEmbed Title:", embed.title)
                print("Embed Description:", embed.description)
            print("-" * 60)
            return self
    
    # Create a mock message with the unusual activity command
    message = MockMessage("Check unusual options activity for TSLA")
    
    # Parse the query 
    parsed = bot.nlp.parse_query(message.content)
    print("Parsed Query:", parsed)
    
    # Skip the actual on_message handler and go straight to handle_unusual_activity_request
    await bot.handle_unusual_activity_request(message, parsed)

# Run the async test
if __name__ == "__main__":
    asyncio.run(test_unusual_activity_command())