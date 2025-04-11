"""
Test script to verify the fix for duplicate LONG-TERM STOP LOSS sections.
This was a bug where the same section appeared twice in the output.
"""

import asyncio
import discord
from discord_bot import OptionsBot, OptionsBotNLP

async def test_long_term_stop_loss():
    """Test the LONG-TERM STOP LOSS formatting fix"""
    print("=" * 50)
    print("TESTING LONG-TERM STOP LOSS FIX")
    print("=" * 50)
    
    # Mock classes for testing
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.author = MockUser()
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            print("RESPONSE:")
            if content:
                print(content)
            if embed:
                print(f"Embed Title: {embed.title}")
                print(f"Embed Description: {embed.description}")
                print("Embed Fields:")
                if hasattr(embed, 'fields'):
                    for i, field in enumerate(embed.fields):
                        print(f"  {i+1}. {field.name}: {field.value}")
                else:
                    print("  No fields")
    
    class MockUser:
        def __init__(self):
            self.id = 12345
            self.name = "TestUser"
            self.mention = "@TestUser"
    
    class MockChannel:
        async def send(self, content=None, embed=None):
            print("CHANNEL RESPONSE:")
            if content:
                print(content)
            if embed:
                print(f"Embed Title: {embed.title}")
                print(f"Embed Description: {embed.description}")
                print("Embed Fields:")
                if hasattr(embed, 'fields'):
                    for i, field in enumerate(embed.fields):
                        print(f"  {i+1}. {field.name}: {field.value}")
                else:
                    print("  No fields")
    
    # Create the bot
    bot = OptionsBot()
    
    # Test 1: Long-term stop loss request
    query1 = "Recommend stop loss for AAPL $220 calls expiring Dec 19 2025"
    message1 = MockMessage(query1)
    
    print("\nTEST 1: Long-term stop loss request")
    print(f"Query: {query1}")
    
    # Process the message
    await bot.handle_message(message1)
    
    # Test 2: Check if mentioning the bot by name works correctly
    query2 = "@OptionsAdvisor recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    message2 = MockMessage(query2)
    
    print("\nTEST 2: Long-term stop loss with mention")
    print(f"Query: {query2}")
    
    # Process the message
    await bot.handle_message(message2)
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    print("\nReview the responses above and verify:")
    print("1. There are no duplicate 'LONG-TERM STOP LOSS' sections")
    print("2. The formatting is correct with a single section")
    print("3. The theta decay warning appears at the bottom (if available)")

if __name__ == "__main__":
    asyncio.run(test_long_term_stop_loss())