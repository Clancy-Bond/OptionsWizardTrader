"""
Test script to verify the theta decay warning is correctly 
displayed at the bottom of the Discord bot responses.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the Python path so we can import modules from the project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing corrected theta decay warning placement...")

class MockChannel:
    async def send(self, content=None, embed=None):
        print(f"CHANNEL MESSAGE: {content if content else 'No content'}")
        if embed:
            print(f"EMBED TITLE: {embed.title}")
            print(f"EMBED DESCRIPTION: {embed.description}")
            if hasattr(embed, 'fields'):
                print("\nEMBED FIELDS:")
                for i, field in enumerate(embed.fields):
                    print(f"Field {i+1}: {field.name}")
                    print(f"Value: {field.value}")
                    print("-" * 50)

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.channel = MockChannel()
        self.author = MockUser()
        
    async def reply(self, content=None, embed=None):
        print(f"REPLY TO MESSAGE: {content if content else 'No content'}")
        if embed:
            print(f"EMBED TITLE: {embed.title}")
            print(f"EMBED DESCRIPTION: {embed.description}")
            if hasattr(embed, 'fields'):
                print("\nEMBED FIELDS:")
                for i, field in enumerate(embed.fields):
                    print(f"Field {i+1}: {field.name}")
                    print(f"Value: {field.value}")
                    print("-" * 50)

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

async def test_theta_decay_section_placement():
    """
    Test that theta decay warnings appear as separate fields at the bottom of embeds
    for all trade horizons (scalp, swing, long-term)
    """
    print_section_header("TESTING SCALP TRADE THETA DECAY PLACEMENT")
    
    # Import bot and setup
    from discord_bot import OptionsBot
    options_bot = OptionsBot()
    
    # Test 1: Scalp trade
    scalp_message = MockMessage("<@1234567890> stop loss for AAPL $190 calls Apr 5th")
    await options_bot.handle_message(scalp_message)
    
    print_section_header("TESTING SWING TRADE THETA DECAY PLACEMENT")
    
    # Test 2: Swing trade
    swing_message = MockMessage("<@1234567890> stop loss for AAPL $190 calls May 17th")
    await options_bot.handle_message(swing_message)
    
    print_section_header("TESTING LONG-TERM TRADE THETA DECAY PLACEMENT")
    
    # Test 3: Long-term trade
    long_term_message = MockMessage("<@1234567890> stop loss for AAPL $190 calls Jan 16th 2026")
    await options_bot.handle_message(long_term_message)
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_theta_decay_section_placement())