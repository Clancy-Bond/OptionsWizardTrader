"""
Test script to verify that the theta decay warning appears at the bottom
of the response for long-term options (instead of in the middle).
"""

import asyncio
import discord
import json
import sys

# Import the bot
from discord_bot import OptionsBot

async def test_long_term_theta_decay():
    """Test function that simulates a long-term option query"""
    # Create a mock message
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.author = MockUser()
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            print(f"REPLY CONTENT: {content}")
            if embed:
                print(f"\nEMBED TITLE: {embed.title}")
                print(f"EMBED DESCRIPTION:\n{embed.description}")
                
                # Check if the theta decay warning is at the bottom
                if "THETA DECAY PROJECTION TO EXPIRY" in embed.description:
                    position = embed.description.find("THETA DECAY PROJECTION TO EXPIRY")
                    print(f"\nPosition of theta decay warning: {position}")
                    print(f"Total length of description: {len(embed.description)}")
                    
                    # If the warning is in the last half of the message, it's likely at the bottom
                    if position > len(embed.description) / 2:
                        print("\n✅ SUCCESS: Theta decay warning appears to be at the bottom of the response")
                    else:
                        print("\n❌ FAILURE: Theta decay warning is not at the bottom of the response")
                else:
                    print("\n❓ No theta decay warning found in the response")
            
            return None
    
    class MockUser:
        def __init__(self):
            self.id = 12345
            self.name = "Test User"
            self.mention = "<@12345>"
    
    class MockChannel:
        async def send(self, content=None, embed=None):
            print(f"CHANNEL SEND: {content}")
            if embed:
                print(f"EMBED: {embed.title}")
            return None
        
        async def typing(self):
            class TypingContextManager:
                async def __aenter__(self):
                    return None
                
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    return None
            
            return TypingContextManager()
    
    # Create the options bot
    options_bot = OptionsBot()
    
    # Test message for long-term options
    message = MockMessage("<@botid> Stop loss for AMD $200 calls expiring January 16 2026")
    
    # Process the message
    response = await options_bot.handle_message(message)
    
    # Log success
    print("\nTest completed!")

def main():
    """Run the test"""
    print("Starting test for long-term option theta decay positioning...")
    asyncio.run(test_long_term_theta_decay())

if __name__ == "__main__":
    main()