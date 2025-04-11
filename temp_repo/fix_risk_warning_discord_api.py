"""
This script fixes the final placement of the risk warning field in discord_bot.py to ensure
it is always the very last field in the embed, appearing after the theta decay projection field.

This version uses methods that are compatible with Discord.py's API.
"""

def fix_risk_warning_placement():
    """
    Update discord_bot.py to ensure risk warning is the absolute last field
    """
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    # First, let's look for all places where we return an embed
    # Right before each one, we'll add code to ensure risk warning is the last field
    
    import re
    return_embed_pattern = r"(\s+)return embed"
    
    def add_risk_warning_before_return(match):
        indent = match.group(1)
        # Use Discord.py API methods to manipulate fields
        return f"{indent}# Ensure risk warning is the very last field\n{indent}# First collect all non-risk warning fields\n{indent}non_risk_fields = []\n{indent}risk_warning_field = None\n{indent}for field in embed.fields:\n{indent}    if hasattr(field, 'name') and '⚠️ RISK WARNING' in field.name:\n{indent}        risk_warning_field = field\n{indent}    else:\n{indent}        non_risk_fields.append(field)\n\n{indent}# Clear all fields\n{indent}embed.clear_fields()\n\n{indent}# Re-add all non-risk warning fields\n{indent}for field in non_risk_fields:\n{indent}    embed.add_field(name=field.name, value=field.value, inline=field.inline)\n\n{indent}# Add risk warning as the final field\n{indent}embed.add_field(\n{indent}    name=\"⚠️ RISK WARNING\",\n{indent}    value=\"Stop losses do not guarantee execution at the specified price in fast-moving markets.\",\n{indent}    inline=False\n{indent})\n{indent}return embed"
    
    modified_content = re.sub(return_embed_pattern, add_risk_warning_before_return, content)
    
    # Write the updated content back to the file
    with open("discord_bot.py", "w") as file:
        file.write(modified_content)
    
    print("✅ Updated discord_bot.py to ensure risk warning is always the last field in the embed")

if __name__ == "__main__":
    fix_risk_warning_placement()