"""
This script fixes the formatting of theta decay warnings in discord_bot.py to ensure
they display correctly at the bottom of Discord embeds.

Key changes:
1. Ensures theta decay warnings appear at the bottom of all responses (after General Risk Note)
2. Fixes the formatting to match the example in test_stop_loss.py
3. Makes sure the theta decay warning name is consistent
4. Cleans up redundant warning symbols in the display text
"""

import re

def fix_theta_decay_formatting():
    """Update the formatting of theta decay warnings in discord_bot.py"""
    print("Fixing theta decay warning formatting...")
    
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Store the original content for comparison
    original_content = content
    
    # Fix 1: Make sure the field name is consistent
    content = re.sub(
        r'name="⚠️ THETA DECAY PROJECTION (?:TO EXPIRY)? ⚠️"',
        r'name="⚠️ THETA DECAY PROJECTION ⚠️"',
        content
    )
    
    # Fix 2: Update how warning message is cleaned when added to the field
    # Old pattern removes too much formatting
    old_clean_pattern = r'value=theta_decay\[\'warning_message\'\]\.replace\("⚠️ \*\*THETA DECAY PROJECTION TO EXPIRY", ""\)\.replace\("⚠️", ""\)'
    
    # New pattern preserves the formatted date and critical warnings
    new_clean_pattern = r'value=theta_decay["warning_message"].replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ THETA DECAY PROJECTION TO").replace("** ⚠️", "")'
    
    content = re.sub(old_clean_pattern, new_clean_pattern, content)
    
    # Fix 3: Ensure theta decay warnings are added after General Risk Note fields
    
    # Pattern for the general risk note followed by field additions
    risk_note_pattern = r'embed\.add_field\(\s*name="⚠️ General Risk Note",.*?inline=False\s*\)'
    
    # When we find a general risk note, ensure the theta decay warning comes after it
    def ensure_theta_decay_after_risk_note(match):
        risk_note = match.group(0)
        
        # Check if there's already a theta decay field after this
        if "name=\"⚠️ THETA DECAY PROJECTION" in risk_note:
            return risk_note
            
        return risk_note + """
                    
                    # Add theta decay warning if available
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ THETA DECAY PROJECTION TO").replace("** ⚠️", ""),
                            inline=False
                        )"""
    
    # Replace matches with the processed content
    content = re.sub(risk_note_pattern, ensure_theta_decay_after_risk_note, content, flags=re.DOTALL)
    
    # Fix 4: Make sure the theta decay warning is properly stored for later use
    # Find places where the warning is directly added to the embed
    direct_add_pattern = r'# If we have a significant warning, add it directly to the description\s*# instead of as a separate field for a more cohesive display\s*if theta_decay\[\'warning_status\'\]:\s*# Add the warning directly to the description for more detailed formatting\s*embed\.description \+= f"\\n\\n{theta_decay\[\'warning_message\'\]}"'
    
    # Replace with code to store the warning for adding at the bottom
    store_warning_code = """# If we have a significant warning, store it for adding at the bottom
                        if theta_decay['warning_status']:
                            # Store the warning message for adding at the bottom
                            theta_decay_warning = theta_decay['warning_message']"""
    
    content = re.sub(direct_add_pattern, store_warning_code, content, flags=re.DOTALL)
    
    # Write the updated content back to the file
    if content != original_content:
        with open('discord_bot.py', 'w') as file:
            file.write(content)
        print("Theta decay warning formatting has been updated!")
    else:
        print("No changes needed for theta decay warning formatting.")

if __name__ == "__main__":
    fix_theta_decay_formatting()