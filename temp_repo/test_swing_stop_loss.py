"""
This script tests specifically the swing trade section of handle_stop_loss_request method
that was previously missing a return statement.
"""
import asyncio
import sys
import discord
import traceback
from discord_bot import OptionsBot

def my_excepthook(type, value, tb):
    print("Exception caught:")
    traceback.print_exception(type, value, tb)
    print("\n")

sys.excepthook = my_excepthook

async def test_swing_stop_loss_request():
    """
    Directly test the handle_stop_loss_request method with a swing trade input
    """
    print("Starting swing trade stop loss test...")
    bot = OptionsBot()
    
    class MockUser:
        def __init__(self, id=123456789):
            self.id = id
            self.name = "TestUser"
            self.mention = f"<@{id}>"
    
    class MockMessage:
        def __init__(self, content, author=None):
            self.content = content
            self.author = author or MockUser()
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            print(f"REPLY: {content}")
            if embed:
                print(f"EMBED TITLE: {embed.title}")
                print(f"EMBED DESCRIPTION: {embed.description}")
                if hasattr(embed, "_fields"):
                    for field in embed._fields:
                        print(f"FIELD: {field['name']} - {field['value']}")
            return self
    
    class MockChannel:
        async def send(self, content=None, embed=None):
            print(f"SEND: {content}")
            if embed:
                print(f"EMBED TITLE: {embed.title}")
                print(f"EMBED DESCRIPTION: {embed.description}")
                if hasattr(embed, "_fields"):
                    for field in embed._fields:
                        print(f"FIELD: {field['name']} - {field['value']}")
            return self
    
    # Test with a swing trade request (this is where the bug was found)
    info = {
        'request_type': 'stop_loss', 
        'ticker': 'AAPL',
        'option_type': 'call',
        'strike': 200,
        'expiration_date': '2025-05-16',  # Make sure this is a valid expiration date
        'premium': 5.0,
        'contracts': 3,
        'target_price': None,  # This will make it a swing trade
        'trade_horizon': None  # Let the method determine this is a swing trade
    }
    
    message = MockMessage("@OptionsBot what's a good stop loss for 3 AAPL $200 calls expiring May 16?")
    
    print("INFO BEING PASSED:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    result = await bot.handle_stop_loss_request(message, info)
    print("RESULT:", result)
    
    if result is None:
        print("WARNING: handle_stop_loss_request returned None")
    else:
        print("SUCCESS: handle_stop_loss_request returned an embed object")
    
    return result

async def main():
    """
    Run the tests
    """
    await test_swing_stop_loss_request()

if __name__ == "__main__":
    asyncio.run(main())