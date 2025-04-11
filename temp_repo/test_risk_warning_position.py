"""
Test script to verify risk warning field position in Discord embeds
"""

import discord
import asyncio

async def test_risk_warning_position():
    """Test if risk warning is positioned correctly at the end of embeds"""
    # Create an actual Discord Embed object
    embed = discord.Embed(
        title="Stop Loss Recommendation",
        description="Here's your stop loss recommendation for AMD calls.",
        color=discord.Color.blue()
    )
    
    # Add some typical fields
    embed.add_field(
        name="📊 Position Details",
        value="AMD $200 Call expiring Jan 16, 2026",
        inline=False
    )
    
    embed.add_field(
        name="💰 Current Price",
        value="$0.99 per contract",
        inline=False
    )
    
    embed.add_field(
        name="🌟 LONG-TERM TRADE STOP LOSS (Weekly chart) 🌟",
        value="• Set a stop loss at $0.45 (54.55% loss)\n• Based on technical analysis and options Greeks",
        inline=False
    )
    
    # Add theta decay field
    embed.add_field(
        name="⏳ Projected Theta Decay (Weekly intervals) ⏳",
        value="• 1 week: -$0.08 (-8.08%)\n• 2 weeks: -$0.15 (-15.15%)\n• 4 weeks: -$0.31 (-31.31%)",
        inline=False
    )
    
    # Add risk warning always as the last field
    embed.add_field(
        name="⚠️ RISK WARNING",
        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
        inline=False
    )
    
    # Check the fields
    print("Fields in order:")
    for i, field in enumerate(embed.fields):
        print(f"Field #{i}: {field.name}")
    
    # Check if risk warning is the last field
    last_field = embed.fields[-1] if embed.fields else None
    if last_field and "RISK WARNING" in last_field.name:
        print("\n✅ Success: RISK WARNING is correctly positioned as the last field")
    else:
        print("\n❌ Error: RISK WARNING is NOT the last field")
        if last_field:
            print(f"Last field is: {last_field.name}")
    
    # Test that we can't directly modify the fields property
    try:
        # This should fail - fields has no setter in discord.py
        embed.fields = [embed.fields[-1]] + embed.fields[:-1]
        print("\n❌ Error: Was able to modify embed.fields directly (unexpected)")
    except Exception as e:
        print(f"\n✅ Expected error: {e}")
        print("This confirms that fields property has no setter, validating our approach")

if __name__ == "__main__":
    asyncio.run(test_risk_warning_position())