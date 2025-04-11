"""
Test to verify the theta decay title formatting is correct.
This should show the date in bold with emojis on both sides.
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

async def test_theta_decay_title_format():
    """Test the theta decay title formatting to ensure it matches the expected format"""
    print_section_header("TESTING THETA DECAY TITLE FORMAT")
    
    bot = OptionsBot()
    
    # Test long-term option to get theta decay warning
    message = MockMessage("Recommend stop loss for AMD $200 calls expiring Jan 16 2026")
    
    # Process the message
    response = await bot.handle_message(message)
    
    # Check if "THETA DECAY PROJECTION" field exists and its format
    theta_field_found = False
    for field in response.fields:
        if "THETA DECAY PROJECTION" in field.name:
            theta_field_found = True
            print("✅ Found theta decay field")
            
            # Check if the value contains a bold title with date and emojis on both sides
            value = field.value
            lines = value.split('\n')
            first_line = lines[0] if lines else ""
            
            print(f"First line: {first_line}")
            
            if "**THETA DECAY PROJECTION TO" in first_line and "**" in first_line:
                print("✅ Found bold title with date")
            else:
                print("❌ Missing bold title format with date")
                
            if first_line.startswith("⚠️") and first_line.endswith("⚠️"):
                print("✅ Found emojis on both sides")
            else:
                print("❌ Missing emojis on both sides")
            
            break
    
    if not theta_field_found:
        print("❌ Theta decay field not found")
        
    return theta_field_found

async def main():
    """Run the tests"""
    print("Testing theta decay title formatting...")
    
    theta_title_test_passed = await test_theta_decay_title_format()
    
    if theta_title_test_passed:
        print("\n✅ Theta decay title formatting test passed!")
    else:
        print("\n❌ Theta decay title formatting test failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())