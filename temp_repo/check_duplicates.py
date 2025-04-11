"""
Simple check for duplicate fields in the Discord embed output.
"""

import discord

def create_test_embed():
    """Create a test embed with all the fields from our method."""
    embed = discord.Embed(
        title="⭐ AMD CALL $200.00 2026-01-16 ⭐",
        color=0x0000FF
    )
    
    # Add the fields in the same order as in the handle_stop_loss_request method
    embed.add_field(
        name="📊 STOP LOSS RECOMMENDATION",
        value="Current Stock Price: $93.80\nCurrent Option Price: $0.99\n• Stock Price Stop Level: $82.54\n• Option Price at Stop: $0.35 (a 64.6% loss)",
        inline=False
    )
    
    embed.add_field(
        name="🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍",
        value="• Ideal For: Options expiring in 3+ months\n• Technical Basis: Major support level with extended volatility buffer",
        inline=False
    )
    
    embed.add_field(
        name="⚠️",
        value="Options typically lose 30-50% of value when the stock hits stop level but have better chance of recovering compared to short-term options.",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ THETA DECAY PROJECTION TO (2026-01-16) ⚠️",
        value="Your option is projected to decay over the next 5 weeks:",
        inline=False
    )
    
    embed.add_field(
        name="",
        value="Week 1 (2025-04-11): $0.91 (-7.8% weekly, -7.8% total)\nWeek 2 (2025-04-18): $0.84 (-8.5% weekly, -15.6% total)\nWeek 3 (2025-04-25): $0.76 (-9.2% weekly, -23.4% total)\nWeek 4 (2025-05-02): $0.68 (-10.2% weekly, -31.2% total)\nWeek 5 (2025-05-09): $0.60 (-11.3% weekly, -39.0% total)\n\nConsider your exit strategy carefully as time decay becomes more significant near expiration.",
        inline=False
    )
    
    # Add the risk warning at the bottom
    embed.add_field(
        name="⚠️ RISK WARNING",
        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
        inline=False
    )
    
    # Check the embed for duplicate fields
    fields_by_name = {}
    for field in embed.fields:
        if field.name not in fields_by_name:
            fields_by_name[field.name] = []
        fields_by_name[field.name].append(field.value)
    
    # Print field counts
    print("Field counts:")
    for name, values in fields_by_name.items():
        print(f"  {name}: {len(values)} occurrence(s)")
        if len(values) > 1:
            print(f"    Values: {values}")
    
    return embed

if __name__ == "__main__":
    create_test_embed()