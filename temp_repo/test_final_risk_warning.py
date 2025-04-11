"""
Final test to verify that the risk warning is always the last field in the embed
"""

import asyncio
import discord

class MockUser:
    def __init__(self):
        self.mention = "@user"

class MockChannel:
    async def send(self, content=None, embed=None):
        print("Channel send called")
        if embed:
            print_embed_fields(embed)
        return None

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
        self.channel = MockChannel()
    
    async def reply(self, content=None, embed=None):
        print("Message reply called")
        if embed:
            print_embed_fields(embed)
        return None

def print_embed_fields(embed):
    """Print all fields in an embed and check if risk warning is last"""
    print(f"\nEmbed Title: {embed.title}")
    print("Fields in order:")
    
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

async def test_risk_warning_direct():
    """Test the risk warning position by directly calling methods"""
    from discord_bot import OptionsBot
    
    bot = OptionsBot()
    
    # Test 1: Test an AMD call stop loss request
    print("\n==== Testing AMD Long-term Call Stop Loss ====")
    message = MockMessage("What's the stop loss for AMD $200 calls expiring in Jan 2026?")
    info = {
        'ticker': 'AMD', 
        'option_type': 'call', 
        'strike': 200.0, 
        'expiration': '2026-01-16',
        'contract_count': 1
    }
    
    try:
        # Directly call handler
        await bot.handle_stop_loss_request(message, info)
    except Exception as e:
        print(f"Error in AMD test: {e}")
    
    # Test 2: Test a TSLA short-term put stop loss request
    print("\n==== Testing TSLA Short-term Put Stop Loss ====")
    message = MockMessage("What's the stop loss for 3 TSLA $190 puts expiring next week?")
    info = {
        'ticker': 'TSLA', 
        'option_type': 'put', 
        'strike': 190.0, 
        'expiration': '2025-04-11',
        'contract_count': 3
    }
    
    try:
        # Use the handle_message method to process the request
        await bot.handle_message(message)
    except Exception as e:
        print(f"Error in TSLA test: {e}")

async def main():
    await test_risk_warning_direct()

if __name__ == "__main__":
    asyncio.run(main())