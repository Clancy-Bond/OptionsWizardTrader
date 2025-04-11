"""
Test that field ordering works correctly for all trade horizons
- Long-term trades (LEAPS): Weekly theta decay intervals 
- Swing trades: 2-day theta decay intervals
- Scalp trades: Daily (1-day) theta decay intervals
"""

import asyncio
import discord
from discord_bot import OptionsBot

async def test_all_trade_horizons():
    """Test field ordering for different trade horizons"""
    
    class MockUser:
        def __init__(self):
            self.mention = "@test_user"
    
    class MockChannel:
        async def send(self, content=None, embed=None):
            print(f"Channel received: {content}")
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
        """Analyze the embed fields ordering"""
        if not hasattr(embed, 'fields'):
            print("Embed has no fields")
            return
        
        print("\n=== EMBED FIELDS ===")
        for i, field in enumerate(embed.fields):
            print(f"Field {i+1}: {field.name}")
            # If this is a theta decay field, print its content too
            if "THETA DECAY" in field.name:
                print(f"  Value: {field.value[:200]}...")
        
        # Check field order
        if len(embed.fields) == 0:
            print("No fields to check")
            return
            
        last_field = embed.fields[-1]
        if "⚠️ RISK WARNING" in last_field.name:
            print("\n✅ SUCCESS: Risk warning is correctly positioned as the last field")
        else:
            print(f"\n❌ ERROR: Risk warning is NOT the last field. Last field is: {last_field.name}")
            
            # Check if risk warning exists at all
            for i, field in enumerate(embed.fields):
                if "⚠️ RISK WARNING" in field.name:
                    print(f"  Risk warning found at position {i+1} (should be last)")
                    
        # Check for theta decay field and ensure it's not the last field
        for i, field in enumerate(embed.fields):
            if "THETA DECAY" in field.name:
                if i == len(embed.fields) - 1:
                    print("❌ ERROR: Theta decay field is the last field (risk warning should be last)")
                else:
                    print(f"✅ SUCCESS: Theta decay field is at position {i+1} (not last)")
    
    # Initialize the bot
    bot = OptionsBot()
    
    print("\n==== Testing long-term trade (LEAPS) ====")
    message = MockMessage("What's the stop loss for MSFT $500 calls expiring Jan 2026?")
    await bot.handle_message(message)
    
    print("\n==== Testing swing trade (2-3 days) ====")
    message = MockMessage("What's the stop loss for TSLA $190 puts expiring in 2 weeks?")
    await bot.handle_message(message)
    
    print("\n==== Testing scalp trade (same day) ====")
    message = MockMessage("What's the stop loss for SPY $465 calls expiring tomorrow?")
    await bot.handle_message(message)
    
if __name__ == "__main__":
    asyncio.run(test_all_trade_horizons())