"""
A simple test to verify the risk warning is properly placed at the end of an embed
This test mocks an embed object and applies our field-reordering logic directly
"""

import discord

def test_risk_warning_placement():
    """
    Test that our field reordering logic correctly places the risk warning at the end
    """
    # Create a test embed with fields in a specific order
    embed = discord.Embed(
        title="Test Stop Loss Recommendation",
        description="This is a test embed",
        color=0x3498DB  # Blue
    )
    
    # Add several fields including a risk warning NOT at the end
    embed.add_field(name="Field 1", value="Value 1", inline=False)
    embed.add_field(name="⚠️ RISK WARNING", value="Risk warning text", inline=False)
    embed.add_field(name="Field 2", value="Value 2", inline=False)
    embed.add_field(name="⏳ THETA DECAY PROJECTION TO (2025-04-25) ⚠️", value="Theta decay values", inline=False)
    
    # Print initial field order
    print("\nInitial field order:")
    for i, field in enumerate(embed.fields):
        print(f"  Field {i+1}: {field.name}")
    
    # Look for risk warning field - should NOT be last initially
    last_field = embed.fields[-1] if embed.fields else None
    if last_field and "RISK WARNING" in last_field.name:
        print("❌ ERROR: Risk warning is already the last field (unexpected)")
    else:
        print(f"✅ Expected: Risk warning is not the last field initially")
        print(f"  Last field is: {last_field.name}")
    
    print("\nApplying field reordering logic...")
    
    # Apply our field reordering logic
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
    
    # Print final field order
    print("\nFinal field order:")
    for i, field in enumerate(embed.fields):
        print(f"  Field {i+1}: {field.name}")
    
    # Check that risk warning is now the last field
    last_field = embed.fields[-1] if embed.fields else None
    if last_field and "RISK WARNING" in last_field.name:
        print("✅ SUCCESS: Risk warning is correctly the last field after reordering")
    else:
        print(f"❌ ERROR: Risk warning is still not the last field after reordering")
        print(f"  Last field is: {last_field.name}")

if __name__ == "__main__":
    test_risk_warning_placement()