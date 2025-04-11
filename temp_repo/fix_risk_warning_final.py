"""
This script fixes the final placement of the risk warning field in discord_bot.py to ensure
it is always the very last field in the embed, appearing after the theta decay projection field.
This version uses a different approach that is compatible with Discord.py's Embed object.
"""

def fix_risk_warning_placement():
    """
    Update discord_bot.py to ensure risk warning is the absolute last field
    """
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    # Instead of trying to modify the fields property directly, we'll just add code
    # to clear all existing risk warnings and add a new one at the end
    
    # Find all "return embed" statements
    # Right before each one, ensure risk warning is the last field added
    
    import re
    return_embed_pattern = r"(\s+)return embed"
    
    def add_risk_warning_before_return(match):
        indent = match.group(1)
        # Add code to remove any existing risk warnings by their name and re-add at the end
        return f"{indent}# Ensure risk warning is the very last field\n{indent}# Remove any existing risk warning by adding fields minus the risk warning field\n{indent}existing_fields = []\n{indent}for field in embed.fields:\n{indent}    if not (hasattr(field, 'name') and '⚠️ RISK WARNING' in field.name):\n{indent}        existing_fields.append(field)\n\n{indent}# Clear all fields\n{indent}embed.clear_fields()\n\n{indent}# Re-add all non-risk warning fields\n{indent}for field in existing_fields:\n{indent}    embed.add_field(name=field.name, value=field.value, inline=field.inline)\n\n{indent}# Add risk warning as the final field\n{indent}embed.add_field(\n{indent}    name=\"⚠️ RISK WARNING\",\n{indent}    value=\"Stop losses do not guarantee execution at the specified price in fast-moving markets.\",\n{indent}    inline=False\n{indent})\n{indent}return embed"
    
    modified_content = re.sub(return_embed_pattern, add_risk_warning_before_return, content)
    
    # Write the updated content back to the file
    with open("discord_bot.py", "w") as file:
        file.write(modified_content)
    
    print("✅ Updated discord_bot.py to ensure risk warning is always the last field in the embed")

if __name__ == "__main__":
    fix_risk_warning_placement()