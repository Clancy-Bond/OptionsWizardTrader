"""
Simplified test script to verify the theta decay warning is correctly
displayed at the bottom of the Discord bot responses.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the Python path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockEmbed:
    def __init__(self, description, title=None, color=None):
        self.description = description
        self.title = title
        self.color = color
        self.fields = []
        
    def add_field(self, name="", value="", inline=False):
        self.fields.append(MockField(name, value, inline))
        return self
        
    def set_footer(self, text=""):
        self.footer = {"text": text}
        return self

class MockField:
    def __init__(self, name, value, inline):
        self.name = name
        self.value = value
        self.inline = inline

class MockChannel:
    async def send(self, content=None, embed=None):
        pass
        
class MockMessage:
    def __init__(self, content):
        self.content = content
        self.channel = MockChannel()
        self.author = MockUser()
        
    async def reply(self, content=None, embed=None):
        if embed:
            print(f"EMBED TITLE: {embed.title}")
            print(f"EMBED FIELDS:")
            for i, field in enumerate(embed.fields):
                print(f"  Field {i+1}: {field.name}")

class MockUser:
    def __init__(self):
        self.id = 12345
        self.name = "Test User"
        self.display_name = "Test User"

def print_section_header(title):
    """Print a section header for better readability in test output"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

async def test_theta_decay_field_placement():
    """
    Test that theta decay warnings appear as separate fields at the bottom of embeds
    """
    from discord_bot import OptionsBot
    bot = OptionsBot()
    
    print_section_header("TESTING THETA DECAY FIELD PLACEMENT")
    
    # Create a custom method to track field ordering
    original_handle_stop_loss = bot.handle_stop_loss_request
    
    async def track_fields(message, info):
        result = await original_handle_stop_loss(message, info)
        
        if hasattr(result, 'fields') and result.fields:
            # Check if theta decay field exists
            theta_fields = [f for f in result.fields if "THETA DECAY" in f.name]
            
            if theta_fields:
                print(f"✅ Found THETA DECAY field at position {len(result.fields) - result.fields[::-1].index(theta_fields[0])}/{len(result.fields)}")
                
                # Check if it's the last substantive field (before footer)
                if result.fields.index(theta_fields[0]) >= len(result.fields) - 2:
                    print("✅ THETA DECAY field is correctly placed at the bottom")
                else:
                    print("❌ THETA DECAY field is NOT at the bottom")
            else:
                print("⚠️ No THETA DECAY field found")
        
        return result
    
    # Replace the method temporarily
    bot.handle_stop_loss_request = track_fields
    
    # Test with different types of options
    test_messages = [
        "<@1234567890> stop loss for TSLA $270 calls expiring Apr 5th 2025",
        "<@1234567890> stop loss for AAPL $190 calls May 17th 2025",
        "<@1234567890> stop loss for AMZN $185 calls January 16th 2026"
    ]
    
    for msg in test_messages:
        print(f"\nTesting: {msg}")
        mock_message = MockMessage(msg)
        await bot.handle_message(mock_message)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(test_theta_decay_field_placement())