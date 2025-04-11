"""
Test risk warning field order using mock objects 
"""

import asyncio
import discord
from discord_bot import OptionsBot

async def test_field_ordering():
    """Test that risk warning is always the last field in embeds"""
    
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
    
    # Initialize the bot
    bot = OptionsBot()
    
    # Test with a manually created embed that includes a risk warning
    embed = discord.Embed(
        title="Test Stop Loss",
        description="Testing field order",
        color=0x3498DB  # Blue
    )
    
    # Add several fields including a risk warning in the middle
    embed.add_field(name="Test Field 1", value="Content 1", inline=False)
    embed.add_field(name="Test Field 2", value="Content 2", inline=False)
    embed.add_field(name="⚠️ RISK WARNING", value="Warning text", inline=False)
    embed.add_field(name="Test Field 3", value="Content 3", inline=False)
    
    # Print fields before reordering
    print("\n=== BEFORE REORDERING ===")
    for i, field in enumerate(embed.fields):
        print(f"Field {i+1}: {field.name}")
    
    # Use our field reordering logic directly
    # First, collect all fields except risk warning
    non_risk_fields = []
    for field in embed.fields:
        if not (hasattr(field, 'name') and '⚠️ RISK WARNING' in field.name):
            non_risk_fields.append(field)
    
    # Clear all fields
    embed.clear_fields()
    
    # Re-add all non-risk fields
    for field in non_risk_fields:
        embed.add_field(name=field.name, value=field.value, inline=field.inline)
    
    # Add risk warning as the final field
    embed.add_field(
        name="⚠️ RISK WARNING",
        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
        inline=False
    )
    
    # Analyze results
    analyze_embed(embed)
    
    # Now test using the bot's handle_stop_loss_request method
    print("\n=== TESTING WITH REAL STOP LOSS REQUEST ===")
    message = MockMessage("What's the stop loss for AAPL $170 calls expiring next Friday?")
    await bot.handle_message(message)
    
if __name__ == "__main__":
    asyncio.run(test_field_ordering())