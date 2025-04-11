"""
Simple test to verify Discord embed field ordering works correctly
"""

import discord
import asyncio

async def test_embed_field_ordering():
    """
    Test that field ordering works with the clear_fields approach
    """
    # Create a simple embed
    embed = discord.Embed(
        title="Test Embed", 
        description="Testing field ordering",
        color=0x00FF00  # Green
    )
    
    # Add some initial fields
    embed.add_field(name="Field 1", value="First field", inline=False)
    embed.add_field(name="Field 2", value="Second field", inline=False)
    embed.add_field(name="⚠️ RISK WARNING", value="Risk warning field", inline=False)
    embed.add_field(name="Field 3", value="Third field", inline=False)
    
    # Print initial field order
    print("\nInitial field order:")
    for i, field in enumerate(embed.fields):
        print(f"  Field {i+1}: {field.name}")
    
    # Move the risk warning to the end
    # First collect all non-risk fields
    non_risk_fields = []
    for field in embed.fields:
        if not (hasattr(field, 'name') and '⚠️ RISK WARNING' in field.name):
            non_risk_fields.append(field)
    
    # Clear all fields
    embed.clear_fields()
    
    # Re-add all non-risk fields
    for field in non_risk_fields:
        embed.add_field(name=field.name, value=field.value, inline=field.inline)
    
    # Add risk warning as the last field
    embed.add_field(
        name="⚠️ RISK WARNING",
        value="Risk warning field",
        inline=False
    )
    
    # Print the final field order
    print("\nFinal field order:")
    for i, field in enumerate(embed.fields):
        print(f"  Field {i+1}: {field.name}")
    
    # Check if risk warning is the last field
    last_field = embed.fields[-1]
    if "⚠️ RISK WARNING" in last_field.name:
        print("\n✅ Success: Risk warning is correctly positioned as the last field")
    else:
        print("\n❌ Error: Risk warning is NOT the last field")

if __name__ == "__main__":
    asyncio.run(test_embed_field_ordering())