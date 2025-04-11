"""
Direct test of the handle_stop_loss_request method to verify it returns an embed
"""

import asyncio
import discord

# Import our bot class from discord_bot.py
from discord_bot import OptionsBot

async def test_stop_loss_handler():
    """Directly test the handle_stop_loss_request method with sample data"""
    print("Testing handle_stop_loss_request with sample data...")
    
    # Create a mock message class
    class MockMessage:
        def __init__(self):
            self.content = "@OptionsBot calculate stop loss for AMD $200 calls expiring Jan 16, 2026"
            self.author = MockUser()
        
        async def reply(self, content=None, embed=None):
            print("\nMock Reply Called with:")
            if content:
                print(f"Content: {content}")
            if embed:
                print(f"Embed Title: {embed.title}")
                print(f"Embed Description: {embed.description}")
                print(f"Embed Color: {embed.color}")
                print("\nEmbed Fields:")
                for field in embed.fields:
                    print(f"  - {field.name}: {field.value}")
                    
    class MockUser:
        def __init__(self):
            self.name = "TestUser"
            self.id = 123456789
    
    # Create sample info dict similar to what the NLP extractor would produce
    test_info = {
        'ticker': 'AMD',
        'option_type': 'call',
        'strike': 200.0,
        'expiration': '2026-01-16',
        'target_price': None,
        'contract_count': 1
    }
    
    # Create an instance of the bot
    bot = OptionsBot()
    
    # Call the method directly with our test data
    mock_message = MockMessage()
    result = await bot.handle_stop_loss_request(mock_message, test_info)
    
    # Validate response
    if result is None:
        print("ERROR: handle_stop_loss_request returned None!")
    else:
        print("\nSUCCESS: handle_stop_loss_request returned an embed object!")
        print(f"Embed title: {result.title}")
        print(f"Number of fields: {len(result.fields)}")
    
    return result is not None

async def main():
    """Run the test"""
    success = await test_stop_loss_handler()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\nTest passed! The stop loss handler is returning an embed as expected.")
    else:
        print("\nTest failed! The stop loss handler is still returning None.")