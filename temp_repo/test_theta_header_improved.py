"""
Test to verify that the theta decay header is properly formatted in Discord embeds
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
        print(f"Channel message: {content}")
        if embed:
            print_theta_fields(embed)

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
        self.channel = MockChannel()

    async def reply(self, content=None, embed=None):
        print(f"Reply message: {content}")
        if embed:
            print_theta_fields(embed)

class MockUser:
    def __init__(self):
        self.id = 12345
        self.name = "TestUser"
        self.display_name = "Test User"

def print_theta_fields(embed):
    """Print all fields in an embed, highlighting theta decay fields"""
    if not hasattr(embed, '_fields'):
        print("No fields in embed")
        return
    
    print("\n=== ALL FIELDS ===")
    for i, field in enumerate(embed._fields):
        print(f"\nField {i}: {field['name']}")
        if "THETA DECAY" in field['name']:
            print("*** THETA DECAY FIELD FOUND ***")
            print(f"  Header format: {field['name']}")
            lines = field['value'].split('\n')
            if lines:
                print(f"  First line: {lines[0]}")
                if len(lines) > 1:
                    print(f"  Second line: {lines[1] if len(lines) > 1 else 'N/A'}")
                
                # Look for pattern of expiration date in field header
                import re
                date_pattern = r"\((\d{4}-\d{2}-\d{2})\)"
                match = re.search(date_pattern, field['name'])
                if match:
                    print(f"  Found date in header: {match.group(1)}")
                    print("  ✅ Date is correctly included in field header")
                else:
                    print("  ❌ No date found in field header")
        else:
            # Just print an excerpt
            print(f"  Value excerpt: {field['value'][:40]}...")

async def test_theta_headers():
    """Test the formatting of theta decay headers in Discord embeds"""
    print_section_header("Testing Theta Decay Headers")
    
    bot = OptionsBot()
    
    # Test with various expiration dates and time frames
    test_queries = [
        "<@12345> What should AAPL $220 calls expiring April 5 be worth?",
        "<@12345> Give me a stop loss for TSLA $270 calls expiring next week",
        "<@12345> What's a good stop loss for SPY $500 calls expiring September?"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n>>> TEST {i+1}: {query}")
        message = MockMessage(query)
        await bot.handle_message(message)

async def main():
    """Run the tests"""
    await test_theta_headers()

if __name__ == "__main__":
    asyncio.run(main())