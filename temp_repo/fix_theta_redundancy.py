"""
This script removes the redundant theta decay projection line from the field content
and puts the date directly in the field name to match the screenshot example.
"""

import re

def fix_theta_redundancy():
    """
    Update the discord_bot.py file to fix the redundancy in theta decay projection display:
    1. Remove the "⚠️ **THETA DECAY PROJECTION TO (date)** ⚠️" line from the field content
    2. Move the date into the field name instead of having a separate first line
    """
    try:
        with open('discord_bot.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Pattern to look for: add_field calls for theta decay warnings
        # We want to replace the field name and remove the redundant first line
        
        # First pattern - handle case where the name is simple and first line has the date
        pattern1 = r'(add_field\(name="⚠️ THETA DECAY PROJECTION ⚠️".*?value=)(f?["\'])⚠️ \*\*THETA DECAY PROJECTION TO \(\{.*?\}\) \*\* ⚠️\\n'
        replacement1 = r'\1\2'
        
        # This should modify field name to include date and remove redundant first line
        modified_content = re.sub(
            r'(add_field\(name=)"⚠️ THETA DECAY PROJECTION ⚠️"(,\s*value=f?".*?)⚠️ \*\*THETA DECAY PROJECTION TO \((.+?)\) \*\* ⚠️\\n', 
            r'\1f"⚠️ THETA DECAY PROJECTION TO ({{\3}}) ⚠️"\2', 
            content, 
            flags=re.DOTALL
        )
        
        # Handle different string quote variations
        modified_content = re.sub(
            r'(add_field\(name=)\'⚠️ THETA DECAY PROJECTION ⚠️\'(,\s*value=f?\'.*?)⚠️ \*\*THETA DECAY PROJECTION TO \((.+?)\) \*\* ⚠️\\n', 
            r'\1f\'⚠️ THETA DECAY PROJECTION TO ({{\3}}) ⚠️\'\2', 
            modified_content, 
            flags=re.DOTALL
        )
        
        # Write the modified content back to the file
        with open('discord_bot.py', 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print("✅ Successfully fixed theta decay redundancy in discord_bot.py")
        
    except Exception as e:
        print(f"❌ Error fixing theta decay redundancy: {e}")

if __name__ == "__main__":
    fix_theta_redundancy()