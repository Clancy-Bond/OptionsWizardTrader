"""
Test stop loss recommendation with fixed risk warning placement
"""

import asyncio
import discord
from discord_bot import OptionsBot

async def test_stop_loss_with_fixed_risk_warning():
    """Test the fixed stop loss request handling"""
    
    class MockUser:
        def __init__(self):
            self.mention = "@user"
    
    class MockChannel:
        async def send(self, content=None, embed=None):
            # Just save the embed for analysis
            return None
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.author = MockUser()
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            # Process and analyze the embed that was returned
            if embed:
                process_embed(embed)
            return None
    
    def process_embed(embed):
        """Check for correct risk warning placement in the embed"""
        print(f"\nAnalyzing embed: {embed.title}")
        
        if not hasattr(embed, 'fields') or len(embed.fields) == 0:
            print("Embed has no fields")
            return
            
        fields = []
        for i, field in enumerate(embed.fields):
            fields.append(field.name)
            print(f"Field #{i+1}: {field.name}")
        
        if "⚠️ RISK WARNING" not in fields:
            print("❌ Error: No Risk Warning field found!")
            return
            
        risk_warning_pos = fields.index("⚠️ RISK WARNING") + 1  # 1-based index for display
        if risk_warning_pos == len(fields):
            print(f"✅ Success: Risk Warning is correctly positioned as the last field ({risk_warning_pos}/{len(fields)})")
        else:
            print(f"❌ Error: Risk Warning is not the last field (position {risk_warning_pos}/{len(fields)})")
    
    # Initialize the bot
    bot = OptionsBot()
    
    # Test various scenarios
    print("\n==== Testing AMD Long-term Call Option ====")
    message = MockMessage("What's the stop loss for AMD $200 calls expiring Jan 2026?")
    await bot.handle_message(message)
    
    print("\n==== Testing TSLA Swing Trade Put Option ====")
    message = MockMessage("What's the stop loss for TSLA $190 puts expiring May 15?")
    await bot.handle_message(message)
    
    print("\n==== Testing AAPL Short-term Call Option ====")
    message = MockMessage("What's the stop loss for AAPL $170 calls expiring this Friday?")
    await bot.handle_message(message)

if __name__ == "__main__":
    asyncio.run(test_stop_loss_with_fixed_risk_warning())