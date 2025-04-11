"""
Test for different intervals of theta decay for various trade horizons
"""

import asyncio
from discord_bot import OptionsBot

class MockChannel:
    async def send(self, content=None, embed=None):
        print("Channel message sent.")

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
        self.channel = MockChannel()

    async def reply(self, content=None, embed=None):
        if embed:
            print("\nRESPONSE EMBED:")
            print(f"Title: {embed.title}")
            print(f"Description: {embed.description}")
            
            # Print fields (focusing on theta decay)
            if hasattr(embed, '_fields'):
                print("\nFields:")
                for i, field in enumerate(embed._fields):
                    name = field['name']
                    # Print all theta decay fields fully
                    if "THETA DECAY" in name:
                        print(f"\n[THETA DECAY FIELD #{i}]")
                        print(f"Name: {name}")
                        value = field['value']
                        print(f"Value: {value}")
                        print("-" * 40)
                    else:
                        # Just print other field names
                        print(f"Field #{i}: {name}")

class MockUser:
    def __init__(self):
        self.id = 12345
        self.name = "TestUser"
        self.display_name = "Test User"

async def test_trade_horizons():
    """Test theta decay intervals for different trade horizons"""
    bot = OptionsBot()
    
    print("\n==== Testing Scalp Trade (daily decay intervals) ====")
    scalp_message = MockMessage("<@12345> Stop loss for SPY $500 calls expiring next Friday")
    await bot.handle_message(scalp_message)
    
    print("\n==== Testing Swing Trade (2-day decay intervals) ====")
    swing_message = MockMessage("<@12345> Stop loss for AAPL $220 calls expiring June 20th, 2025")
    await bot.handle_message(swing_message)
    
    print("\n==== Testing Long-Term Trade (weekly decay intervals) ====")
    longterm_message = MockMessage("<@12345> Stop loss for TSLA $370 calls expiring January 16, 2026")
    await bot.handle_message(longterm_message)

async def main():
    await test_trade_horizons()

if __name__ == "__main__":
    asyncio.run(main())