"""
This script correctly modifies the Discord bot to move the theta decay warning from
being part of the embed description to being a separate field that appears
at the bottom of the embed.

The previous fix attempted to use string replacement which might not have properly matched
the current code, as the code might have been updated since the fix was written.
"""

import re

def apply_fix():
    """Apply the fix to move theta decay warning from description to field in discord_bot.py"""
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Find all instances of adding to description and replace with adding as field
    replacements = [
        (
            r"# If we have a significant warning, add it directly to the description\n"
            r"\s+# instead of as a separate field for a more cohesive display\n"
            r"\s+if theta_decay\['warning_status'\]:\n"
            r"\s+# Add the warning directly to the description for more detailed formatting\n"
            r"\s+embed\.description \+= f\"\\n\\n{theta_decay\['warning_message'\]}\"",
            
            "# If we have a significant warning, add it as a separate field\n"
            "                        if theta_decay['warning_status']:\n"
            "                            embed.add_field(\n"
            "                                name=\"⚠️ THETA DECAY PROJECTION ⚠️\",\n"
            "                                value=theta_decay['warning_message'].replace(\"⚠️ **THETA DECAY PROJECTION TO EXPIRY\", \"\").replace(\"⚠️\", \"\"),\n"
            "                                inline=False\n"
            "                            )"
        )
    ]
    
    # Apply each replacement
    modified_content = content
    for old, new in replacements:
        modified_content = re.sub(old, new, modified_content)
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(modified_content)
    
    print("Successfully moved theta decay warnings from description to fields.")

if __name__ == "__main__":
    apply_fix()