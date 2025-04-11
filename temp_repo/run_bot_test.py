"""
Simple test script to verify the Discord bot responses to various stop loss queries.
"""
import os
import asyncio
import types
import sys
from datetime import datetime

# Mock discord module for testing without actual Discord connection
class MockDiscord:
    def __init__(self):
        self.Embed = self.MockEmbed
        self.Object = self.MockObject
        self.Color = self.MockColor
        
    class MockObject:
        def __init__(self, id):
            self.id = id
            
    class MockColor:
        @staticmethod
        def blue():
            return 0x368BD6
            
        @staticmethod
        def green():
            return 0x00D026
            
        @staticmethod
        def orange():
            return 0xFF9500
            
    class MockEmbed:
        def __init__(self, title="", description="", color=None):
            self.title = title
            self.description = description
            self.color = color or 0
            self.fields = []
            self.footer = None
            
        def add_field(self, name="", value="", inline=False):
            self.fields.append(types.SimpleNamespace(
                name=name,
                value=value,
                inline=inline
            ))
            return self
            
        def set_footer(self, text=""):
            self.footer = types.SimpleNamespace(text=text)
            return self

discord = MockDiscord()

# Import the bot from discord_bot.py
sys.path.append('.')
from discord_bot import OptionsBot

async def test_queries():
    """Test the bot with various queries"""
    bot = OptionsBot()
    
    # Test queries
    queries = [
        "What's the stop loss for AAPL $200 calls expiring Jan 15th 2026?",
        "Where should I set my stop loss for 3 TSLA $250 puts expiring next week?",
        "Can you recommend a stop loss for my MSFT $430 calls expiring tomorrow?",
        "Stop loss for 2 NVDA $900 calls expiring in June?",
        "Exit point for my AMD $165 puts expiring in 3 months?"
    ]
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.author = discord.Object(id=123456789)
            
            class MockChannel:
                async def send(self, *args, **kwargs):
                    return None
            
            self.channel = MockChannel()
            
            # For logging
            print(f"\n----- Processing query: {content} -----")
            
        async def reply(self, content=None, embed=None, mention_author=False):
            # Just acknowledge the reply happened
            print(f"Bot replied: {'with content' if content else 'no content'}, {'with embed' if embed else 'no embed'}")
            
            # Print more details about the embed if available
            if embed:
                print(f"Embed title: {embed.title}")
                print(f"Embed color: {hex(embed.color.value) if hasattr(embed.color, 'value') else embed.color}")
                print(f"Number of fields: {len(embed.fields)}")
                
                # Print the first few field names
                for i, field in enumerate(embed.fields[:3]):
                    print(f"Field {i+1}: {field.name}")
                    
            return None
    
    # Process each query
    for query in queries:
        # Create a mock message
        message = MockMessage(query)
        
        # Send to the bot's handle_message method
        await bot.handle_message(message)
        
        # Add some space between queries
        print("\n" + "-" * 50)

# Run the test
async def main():
    await test_queries()

if __name__ == "__main__":
    asyncio.run(main())