"""
Test to verify that the theta decay warning is moved from the embed description
to a separate field in the Discord embed.
"""

import asyncio
import sys
from discord_bot import OptionsBot, OptionsBotNLP

def print_section_header(title):
    """Print a section header for better readability in test output"""
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50 + "\n")

class MockChannel:
    async def send(self, content=None, embed=None):
        if embed:
            print("EMBED RESPONSE:")
            print(f"Title: {embed.title}")
            print(f"Description: {embed.description}")
            print("\nFIELDS:")
            for i, field in enumerate(embed.fields):
                print(f"Field {i+1}: {field.name}")
                print(f"Value: {field.value}")
                print()
        return None

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.channel = MockChannel()
        self.author = MockUser()
        
    async def reply(self, content=None, embed=None):
        if embed:
            print("EMBED RESPONSE:")
            print(f"Title: {embed.title}")
            print(f"Description: {embed.description}")
            print("\nFIELDS:")
            for i, field in enumerate(embed.fields):
                print(f"Field {i+1}: {field.name}")
                print(f"Value: {field.value}")
                print()
        return None

class MockUser:
    def __init__(self):
        self.id = "12345"
        self.name = "Test User"
        self.mention = "@Test User"

async def test_long_term_theta_decay_placement():
    """Test that the LONG-TERM theta decay warning is placed in a separate field"""
    print_section_header("TESTING LONG-TERM THETA DECAY PLACEMENT")
    
    bot = OptionsBot()
    
    # Test message for long-term trade (LEAPS)
    message = MockMessage("Recommend stop loss for AAPL $220 calls expiring Dec 19 2025")
    
    # Process the message
    response = await bot.handle_message(message)
    
    # Check if "THETA DECAY PROJECTION" appears in the fields
    has_theta_field = False
    for field in response.fields:
        if "THETA DECAY PROJECTION" in field.name:
            has_theta_field = True
            print("✅ Found theta decay warning as a field!")
            break
    
    if not has_theta_field:
        print("❌ Theta decay warning is NOT properly placed in a field")
        # Check if it's still in the description
        if "THETA DECAY PROJECTION" in response.description:
            print("❌ Theta decay warning is still in the description!")
    
    return has_theta_field

async def main():
    """Run the tests"""
    print("Testing theta decay warning placement in Discord embeds...")
    
    long_term_test_passed = await test_long_term_theta_decay_placement()
    
    if long_term_test_passed:
        print("\n✅ All tests passed! The theta decay warnings are correctly placed in fields.")
    else:
        print("\n❌ Test failed! The theta decay warnings are not correctly placed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())