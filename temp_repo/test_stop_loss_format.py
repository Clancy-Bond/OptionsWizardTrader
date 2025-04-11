"""
Test script to verify the stop loss formatting in the Discord bot.
This script directly calls the handle_stop_loss_request method with
the parameters we want to test.
"""

import discord
import asyncio
from datetime import datetime, timedelta
import sys

# Add parent directory to path for imports
sys.path.insert(0, '.')

from discord_bot import OptionsBot

async def test_stop_loss_formatting():
    # Create OptionsBot instance
    bot = OptionsBot()
    
    # Create mock message
    class MockMessage:
        def __init__(self):
            self.content = "Recommend stop loss for AMD $200 calls expiring Jan 16th 2026"
            self.author = MockUser()
        
        async def reply(self, content=None, embed=None):
            print("REPLY:", content)
            print_embed(embed)
            return None
    
    class MockUser:
        def __init__(self):
            self.id = 12345
            self.name = "TestUser"
    
    # Test info dict
    info = {
        'ticker': 'AMD',
        'option_type': 'call',
        'strike_price': 200.00,
        'expiration': datetime(2026, 1, 16),
        'request_type': 'stop_loss',
        'contracts': 1
    }
    
    # Call the method
    result = await bot.handle_stop_loss_request(MockMessage(), info)
    
    return result

def print_embed(embed):
    """Pretty print an embed object"""
    if not embed:
        print("No embed found!")
        return
    
    print("\n==== EMBED CONTENTS ====")
    print(f"Title: {embed.title}")
    print(f"Description: {embed.description}")
    print(f"Color: {embed.color}")
    
    print("\n=== FIELDS ===")
    for i, field in enumerate(embed.fields):
        print(f"Field {i+1}: {field.name}")
        print(f"Value: {field.value}")
        print(f"Inline: {field.inline}")
        print("-" * 30)
    
    if embed.footer:
        print(f"Footer: {embed.footer.text}")

if __name__ == "__main__":
    # Run the async test
    loop = asyncio.get_event_loop()
    embed = loop.run_until_complete(test_stop_loss_formatting())
    
    # Final verification
    print("\n==== FINAL VERIFICATION ====")
    if embed and embed.title and "AMD CALL $200.00 2026-01-16" in embed.title:
        print("✅ Title format is correct")
    else:
        print("❌ Title format is incorrect")
        
    # Check for fields
    if embed and any("THETA DECAY PROJECTION" in field.name for field in embed.fields):
        print("✅ Theta decay projection is present")
    else:
        print("❌ Theta decay projection is missing")
        
    # Check order of fields
    risk_warning_idx = None
    theta_decay_idx = None
    
    for i, field in enumerate(embed.fields):
        if "RISK WARNING" in field.name:
            risk_warning_idx = i
        if "THETA DECAY PROJECTION" in field.name:
            theta_decay_idx = i
            
    if risk_warning_idx is not None and theta_decay_idx is not None:
        if risk_warning_idx > theta_decay_idx:
            print("✅ Risk warning appears after theta decay projection")
        else:
            print("❌ Risk warning appears before theta decay projection")
    else:
        print("❓ Could not determine field order")