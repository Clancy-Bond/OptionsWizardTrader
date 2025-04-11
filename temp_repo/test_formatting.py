"""
Test script to directly verify the expiration date formatting in handle_stop_loss_request.
"""

import discord
import asyncio
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, '.')

from discord_bot import OptionsBot

async def test_date_formatting():
    """Test the date formatting to ensure it's in YYYY-MM-DD format"""
    # Create OptionsBot instance
    bot = OptionsBot()
    
    # Create mock message
    class MockMessage:
        def __init__(self):
            self.content = "Recommend stop loss for AMD $200 calls expiring Jan 16th 2026"
            self.author = MockUser()
        
        async def reply(self, content=None, embed=None):
            print("REPLY:", content)
            if embed:
                print_embed(embed)
            return None
    
    class MockUser:
        def __init__(self):
            self.id = 12345
            self.name = "TestUser"
    
    # Test info dict with expiration date in January
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
    
    # Test with an April date
    info2 = {
        'ticker': 'TSLA',
        'option_type': 'call',
        'strike_price': 270.00,
        'expiration': datetime(2025, 4, 4),
        'request_type': 'stop_loss',
        'contracts': 1
    }
    
    # Call the method again
    print("\n\n==== Testing with April date ====\n")
    result2 = await bot.handle_stop_loss_request(MockMessage(), info2)
    
    return result, result2

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
    embeds = loop.run_until_complete(test_date_formatting())
    
    # Final verification
    print("\n==== FINAL VERIFICATION ====")
    
    # Check January date
    if embeds[0] and embeds[0].title and "2026-01-16" in embeds[0].title:
        print("✅ January date format is correct (2026-01-16)")
    else:
        print("❌ January date format is incorrect")
    
    # Check April date
    if embeds[1] and embeds[1].title and "2025-04-04" in embeds[1].title:
        print("✅ April date format is correct (2025-04-04)")
    else:
        print("❌ April date format is incorrect")