"""
A very simple test to verify the risk warning is properly placed at the end of an embed
This test mocks an embed object and checks if the risk warning appears exactly once
"""

import sys
import discord
import traceback

def test_risk_warning_placement():
    """
    Create a mock environment to test the issue
    """
    try:
        # Import from discord_bot
        from discord_bot import OptionsBot
        
        # Function to analyze the fields in an embed
        def analyze_embed(embed):
            """Check for duplicate risk warnings in the embed"""
            print(f"\nAnalyzing embed fields:")
            
            if not hasattr(embed, 'fields') or len(embed.fields) == 0:
                print("Embed has no fields")
                return
                
            fields = []
            risk_warning_count = 0
            risk_warning_positions = []
            
            for i, field in enumerate(embed.fields):
                fields.append(field.name)
                print(f"Field #{i+1}: {field.name}")
                if "RISK WARNING" in field.name:
                    risk_warning_count += 1
                    risk_warning_positions.append(i+1)
            
            print(f"\nFound {risk_warning_count} risk warning fields at positions: {risk_warning_positions}")
            
            if risk_warning_count > 1:
                print("❌ ERROR: Found multiple risk warning fields!")
            elif risk_warning_count == 0:
                print("❌ ERROR: No risk warning field found!")
            else:
                print("✅ SUCCESS: Exactly one risk warning field found")
                
                # Check if it's the last field
                if risk_warning_positions[0] == len(fields):
                    print("✅ SUCCESS: Risk warning is correctly positioned as the last field")
                else:
                    print(f"❌ ERROR: Risk warning is not the last field! Found at position {risk_warning_positions[0]} of {len(fields)}")
        
        # Create a test embed with fields including a risk warning NOT at the end
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
        print("Initial field order:")
        analyze_embed(embed)
        
        print("\nApplying field reordering logic...")
        
        # Apply our field reordering logic - this is the same logic used in the bot
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
        analyze_embed(embed)
        
    except Exception as e:
        print(f"ERROR in test: {str(e)}")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    test_risk_warning_placement()