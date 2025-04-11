"""
Direct test of the field order in stop loss embeds, with a focus on risk warning placement
"""

import asyncio
import discord
from discord_bot import OptionsBot

async def test_field_order():
    """Test stop loss field order directly"""
    bot = OptionsBot()
    
    print("==== Testing AMD Long-term Call Stop Loss ====")
    test_info = {
        'ticker': 'AMD', 
        'option_type': 'call', 
        'strike': 200.0, 
        'expiration': '2026-01-16',
        'contract_count': 1
    }
    
    # Create a mock message
    class MockMessage:
        def __init__(self):
            class MockUser:
                def __init__(self):
                    self.mention = "@user"
            self.author = MockUser()
    
    message = MockMessage()
    
    try:
        # Direct call to handle_stop_loss_request
        embed = await bot.handle_stop_loss_request(message, test_info)
        
        # Manually inspect field order
        print("\nFields in order:")
        for i, field in enumerate(embed.fields):
            print(f"Field #{i}: {field.name}")
        
        # Check risk warning position
        last_field = embed.fields[-1] if embed.fields else None
        if last_field and "RISK WARNING" in last_field.name:
            print("\n✅ Success: RISK WARNING is correctly positioned as the last field")
        else:
            print("\n❌ Error: RISK WARNING is NOT the last field")
            if last_field:
                print(f"Last field is: {last_field.name}")
            else:
                print("No fields found in the embed")
    
    except Exception as e:
        print(f"Error during testing: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_field_order())