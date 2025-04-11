"""
Test to verify that the redundancy in theta decay sections has been fixed.
This should show the date directly in the field name and no redundant first line in content.
"""

import asyncio
import discord
import datetime
from discord_bot import OptionsBot

def print_section_header(title):
    """Print a section header for better readability in test output"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

class MockChannel:
    async def send(self, content=None, embed=None):
        if content:
            print(f"Channel message: {content}")
        if embed:
            print_theta_decay_fields(embed)

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
        self.channel = MockChannel()

    async def reply(self, content=None, embed=None):
        if content:
            print(f"Reply message: {content}")
        if embed:
            print_theta_decay_fields(embed)

class MockUser:
    def __init__(self):
        self.id = 12345
        self.name = "TestUser"
        self.display_name = "Test User"

def print_theta_decay_fields(embed):
    """Print only the theta decay fields from an embed"""
    if not hasattr(embed, '_fields'):
        print("No fields in embed")
        return
    
    found = False
    for field in embed._fields:
        if "THETA DECAY PROJECTION" in field['name']:
            found = True
            print("\n=== THETA DECAY FIELD FOUND ===")
            print(f"Field name: {field['name']}")
            print("Field value first 100 chars: " + field['value'][:100].replace('\n', '\\n') + "...")
    
    if not found:
        print("No theta decay fields found in embed")

async def test_theta_redundancy_fix():
    """Test that the theta decay redundancy is fixed"""
    print_section_header("Testing Theta Decay Field Formatting")
    
    bot = OptionsBot()
    
    # Test with an option price request
    print("\n>>> TEST 1: Option Price Request")
    message = MockMessage("<@12345> What should TSLA $270 calls expiring Apr 5 be trading at?")
    await bot.handle_message(message)
    
    # Test with a stop loss request
    print("\n>>> TEST 2: Stop Loss Request")
    message = MockMessage("<@12345> Give me a stop loss for AAPL $225 calls expiring Apr 12")
    await bot.handle_message(message)
    
    # Test with unusual activity request
    print("\n>>> TEST 3: LEAPS Option Request")
    message = MockMessage("<@12345> What should SPY $505 calls expiring Sep 19 be trading at?")
    await bot.handle_message(message)

async def main():
    """Run the tests"""
    await test_theta_redundancy_fix()

if __name__ == "__main__":
    asyncio.run(main())