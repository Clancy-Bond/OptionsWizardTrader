"""
Test file to verify that the theta decay projection formatting is now correct
with the date appearing in the field name and no redundant information
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
        print(f"Channel message sent: {content}")
        if embed:
            print_embed_details(embed)

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
        self.channel = MockChannel()

    async def reply(self, content=None, embed=None):
        print(f"Reply message sent: {content}")
        if embed:
            print_embed_details(embed)

class MockUser:
    def __init__(self):
        self.id = 12345
        self.name = "TestUser"
        self.display_name = "Test User"

def print_embed_details(embed):
    """Print the details of a Discord embed object"""
    print("\nEmbed Details:")
    print(f"Title: {embed.title}")
    print(f"Description: {embed.description}")
    
    if hasattr(embed, '_fields'):
        print("\nFields:")
        for field in embed._fields:
            print(f"\n[Field] {field['name']}")
            print(f"{field['value']}")
            print(f"Inline: {field['inline']}")
    
    if hasattr(embed, 'footer'):
        print(f"\nFooter: {embed.footer.text}")

async def test_theta_format():
    """Test that the theta decay format is correct"""
    print_section_header("Testing Theta Decay Format")
    
    bot = OptionsBot()
    
    # Test with a mid-term option price request
    message = MockMessage("<@12345> What should TSLA $270 calls expiring Apr 30 be trading at?")
    await bot.handle_message(message)
    
    # Test with a stop loss request
    message = MockMessage("<@12345> Give me a stop loss for AAPL $225 calls expiring May 15")
    await bot.handle_message(message)

async def main():
    """Run the tests"""
    await test_theta_format()

if __name__ == "__main__":
    asyncio.run(main())