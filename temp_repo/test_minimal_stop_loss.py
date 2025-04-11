"""
Minimal test for handle_stop_loss_request that directly calls the method with
the bare minimum data needed for it to process a swing trade request
"""
import asyncio
import sys
import traceback
from discord_bot import OptionsBot

def my_excepthook(type, value, tb):
    print("Exception caught:")
    traceback.print_exception(type, value, tb)
    print("\n")

sys.excepthook = my_excepthook

async def test_minimal_stop_loss():
    """
    Create a minimal test case for handle_stop_loss_request
    """
    print("Starting minimal stop loss test...")
    
    # Initialize the bot
    bot = OptionsBot()
    
    class MockUser:
        def __init__(self, id=123456789):
            self.id = id
            self.name = "TestUser"
            self.mention = f"<@{id}>"
    
    class MockMessage:
        def __init__(self):
            self.content = "@OptionsBot stop loss TSLA $275 calls expiring next Friday"
            self.author = MockUser()
            # We'll add channel attribute during testing if needed
        
        async def reply(self, content=None, embed=None):
            print("MOCK REPLY CALLED")
            print(f"CONTENT: {content}")
            if embed:
                print(f"EMBED TITLE: {embed.title}")
                print(f"EMBED DESCRIPTION: {embed.description}")
                if hasattr(embed, "_fields"):
                    for field in embed._fields:
                        print(f"FIELD: {field['name']} - {field['value']}")
            return self
    
    # Create the minimal info dictionary needed
    info = {
        'request_type': 'stop_loss',
        'ticker': 'TSLA',
        'option_type': 'call',
        'strike': 275.0,
        'expiration': '2025-04-11',  # Next Friday from April 4, 2025
        'premium': 10.00,  # Default premium
        'contracts': 1,    # Default contracts
        'trade_horizon': 'swing',  # Explicitly set to swing trade
        'target_price': None    # No target price to ensure swing trade path
    }
    
    message = MockMessage()
    
    print("INFO PASSED TO HANDLE_STOP_LOSS_REQUEST:")
    for k, v in info.items():
        print(f"  {k}: {v}")
    
    print("\nCalling handle_stop_loss_request...\n")
    try:
        # Call the method directly with our minimal test data
        result = await bot.handle_stop_loss_request(message, info)
        
        # Check the result
        print("\nRESULT:", result)
        
        if result is None:
            print("ERROR: handle_stop_loss_request returned None")
        else:
            print("SUCCESS: handle_stop_loss_request returned an embed object")
    
    except Exception as e:
        print(f"ERROR: Exception during test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimal_stop_loss())