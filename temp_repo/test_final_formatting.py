"""
Test script to verify the final formatting of stop loss requests.
"""

import discord
import asyncio
from discord_bot import OptionsBot

async def test_stop_loss_request():
    """Test a stop loss request with the AMD example from the screenshot."""
    
    # Create a mock message and user
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.author = MockUser()
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            print("MOCK REPLY:")
            if content:
                print(content)
            if embed:
                print(f"EMBED TITLE: {embed.title}")
                print(f"EMBED DESCRIPTION: {embed.description if hasattr(embed, 'description') else 'No description'}")
                print("EMBED FIELDS:")
                for field in embed.fields:
                    print(f"  - {field.name}: {field.value}")
            return self
    
    class MockUser:
        def __init__(self):
            self.id = 123456789
            self.name = "Test User"
            self.discriminator = "1234"
            self.display_name = "Test User"
    
    class MockChannel:
        async def send(self, content=None, embed=None):
            print("MOCK CHANNEL SEND:")
            if content:
                print(content)
            if embed:
                print(f"EMBED TITLE: {embed.title}")
                print(f"EMBED DESCRIPTION: {embed.description if hasattr(embed, 'description') else 'No description'}")
                print("EMBED FIELDS:")
                for field in embed.fields:
                    print(f"  - {field.name}: {field.value}")
            return self
    
    # Create a message with the same content as in the screenshot
    message = MockMessage("<@1354551896605589584> AMD calls, strike price 200$ expiring Jan 16th, 2026 stop loss reccomendation?")
    
    # Create the bot instance
    bot = OptionsBot()
    
    # Parse the query
    request_type, info = bot.nlp.parse_query(message.content)
    print(f"Parsed info: {info}")
    
    # Call the handle_stop_loss_request method
    embed = await bot.handle_stop_loss_request(message, info)
    
    # Check the embed fields
    risk_warning_count = 0
    for field in embed.fields:
        if field.name == "⚠️ RISK WARNING":
            risk_warning_count += 1
            print(f"Found risk warning field: {field.value}")
    
    print(f"Total risk warning fields: {risk_warning_count}")
    
    # Check that there's only one risk warning
    assert risk_warning_count == 1, f"Expected 1 risk warning, found {risk_warning_count}"
    
    print("Test passed successfully!")
    return embed

if __name__ == "__main__":
    asyncio.run(test_stop_loss_request())