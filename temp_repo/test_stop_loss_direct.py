"""
Direct test of stop loss recommendations for field order verification
"""

import asyncio
from discord_bot import OptionsBot

class MockUser:
    def __init__(self):
        self.mention = "@user"

class MockChannel:
    async def send(self, content=None, embed=None):
        if embed:
            analyze_embed(embed)
        return None

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
        self.channel = MockChannel()
    
    async def reply(self, content=None, embed=None):
        if embed:
            analyze_embed(embed)
        return None

def analyze_embed(embed):
    """Analyze embed fields to check correct risk warning placement"""
    print(f"\nEmbed Title: {embed.title}")
    print(f"Embed Description: {embed.description[:50]}...")
    
    print("\nFields in order:")
    field_names = []
    for i, field in enumerate(embed.fields):
        print(f"Field #{i}: {field.name}")
        field_names.append(field.name)
    
    if "⚠️ RISK WARNING" in field_names:
        if field_names[-1] == "⚠️ RISK WARNING":
            print("\n✅ SUCCESS: Risk warning is correctly positioned as the LAST field")
        else:
            position = field_names.index("⚠️ RISK WARNING") + 1
            total = len(field_names)
            print(f"\n❌ ERROR: Risk warning is field #{position}/{total} instead of last")
    else:
        print("\n❌ ERROR: No risk warning field found")

async def test_different_trade_horizons():
    """Test field order for different trade horizons"""
    bot = OptionsBot()
    
    print("\n==== Testing TSLA Short-term Scalp Trade ====")
    message = MockMessage("<@123456> What's the stop loss for TSLA $190 puts expiring tomorrow?")
    await bot.handle_message(message)
    
    print("\n==== Testing AMD Medium-term Swing Trade ====")
    message = MockMessage("<@123456> What's the stop loss for AMD $180 calls expiring May 15th?")
    await bot.handle_message(message)
    
    print("\n==== Testing AAPL Long-term LEAPS Trade ====")
    message = MockMessage("<@123456> What's the stop loss for AAPL $220 calls expiring Jan 2026?")
    await bot.handle_message(message)

if __name__ == "__main__":
    asyncio.run(test_different_trade_horizons())