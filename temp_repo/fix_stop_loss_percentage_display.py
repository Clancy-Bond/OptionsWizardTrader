"""
Fix script to ensure the dynamic buffer percentage is properly displayed in the stop loss recommendation text.

This script addresses the issue where the stop loss recommendation text doesn't show the percentage 
difference from the current price, which should vary dynamically based on days to expiration.
"""

def fix_stop_loss_percentage_display():
    """Fix the stop loss percentage display in the discord_bot.py file."""
    import re
    
    # Read the discord_bot.py file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Look for the section where we add the stock price stop level field
    # Current pattern: we add the field but don't include the percentage
    pattern = r'(\s+)embed\.add_field\(\s*name="Stock Price Stop Level",\s*value=f"\${(.*?):.2f}",\s*inline=True\s*\)'
    
    # Replacement pattern: include the percentage calculation based on option_type and current_price
    if "option_type.lower() == 'call'" in content:
        replacement = r'\1# Calculate percentage based on option type\n\1percentage_diff = ((current_price - \2) / current_price) * 100 if option_type.lower() == "call" else ((\2 - current_price) / current_price) * 100\n\1percentage_text = f"({percentage_diff:.1f}% below current)" if option_type.lower() == "call" else f"({percentage_diff:.1f}% above current)"\n\1embed.add_field(\n\1    name="Stock Price Stop Level",\n\1    value=f"${\\2:.2f} {percentage_text}",\n\1    inline=True\n\1)'
    else:
        # If the pattern is different, we need a different approach
        print("Could not find the expected pattern in discord_bot.py. Manual review needed.")
        return
    
    # Replace the pattern in the content
    updated_content = re.sub(pattern, replacement, content)
    
    # Check if the content was actually updated
    if updated_content == content:
        print("No changes were made. Could not find the pattern to replace.")
        
        # Try an alternative approach - look for field adding for "Stock Price Stop Level"
        field_pattern = r'name="Stock Price Stop Level",\s*value=f"\${([^}]+)}'
        field_matches = re.findall(field_pattern, content)
        
        if field_matches:
            print(f"Found field pattern matches: {field_matches}")
            
            # Try a more targeted replacement
            for match in field_matches:
                simple_pattern = rf'name="Stock Price Stop Level",\s*value=f"\${match}' 
                simple_replacement = f'name="Stock Price Stop Level",\s*value=f"${match} ({{percentage_diff:.1f}}% {"below" if option_type.lower() == "call" else "above"} current)"'
                updated_content = re.sub(simple_pattern, simple_replacement, updated_content)
        else:
            print("Could not find any 'Stock Price Stop Level' field patterns.")
    else:
        print("Successfully updated the stop loss percentage display.")
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    # Now let's also check technical_analysis.py to make sure the percentage is included there
    with open('technical_analysis.py', 'r') as file:
        technical_content = file.read()
    
    # Additional updates to ensure percentage is in the recommendation
    # This is a fallback if the discord_bot.py change doesn't work
    
    print("Checking if stop loss recommendations in technical_analysis.py include percentages...")
    
    # Make sure each stop level value includes a percentage display
    # These patterns check for specific cases that might miss percentage displays
    patterns_to_check = [
        r'Stock Price Stop Level: \${stop_loss:.2f}\)',
        r'Stock Price Stop Level: \${stop_loss:.2f}\s+\(',
        r'Stock Price Stop Level: \${stop_loss:.2f}"',
    ]
    
    for pattern in patterns_to_check:
        if re.search(pattern, technical_content):
            print(f"Found potential missing percentage pattern: {pattern}")
            # We found a pattern that might be missing the percentage
            # You would add specific fixes here

    print("Finished checking technical_analysis.py")

if __name__ == "__main__":
    fix_stop_loss_percentage_display()