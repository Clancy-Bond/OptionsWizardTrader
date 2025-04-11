"""
This script fixes the final placement of the risk warning field in discord_bot.py to ensure
it is always the very last field in the embed, appearing after the theta decay projection field.
"""

def fix_risk_warning_placement():
    """
    Update discord_bot.py to ensure risk warning is the absolute last field
    """
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    # Find all instances where theta decay fields are added
    # Look for patterns where risk warning might be added before theta decay
    
    # Pattern 1: Find places where risk warning is added before theta decay
    import re
    
    # Update the pattern for risk warning placement in all trade horizons
    modified_content = content
    
    # Define patterns for each trade horizon section
    patterns = [
        # Check each trade horizon section where theta decay and risk warning are added
        (r"(# Add expiry-specific theta decay warning.*?theta_decay_warning\s*=\s*\".*?\"\s*# Add Risk Warning.*?embed\.add_field\(\s*name=\"⚠️ RISK WARNING\".*?inline=False\s*\))(.*?)(# Add the theta decay field.*?theta_decay_warning.*?inline=False\s*\))",
         r"\3\2\1"),  # Move risk warning after theta decay
        
        # For long-term trades
        (r"(# Add the theta decay field.*?theta_decay_warning.*?inline=False\s*\))(.*?)(# Add Risk Warning.*?embed\.add_field\(\s*name=\"⚠️ RISK WARNING\".*?inline=False\s*\))",
         r"\1\2\3"),  # Keep order if already correct
        
        # For any other cases where risk warning might be added before theta decay
        (r"(# Store theta decay warning for later placement at the bottom.*?theta_decay_warning\s*=\s*\".*?\")(.*?)(# Add Risk Warning.*?embed\.add_field\(\s*name=\"⚠️ RISK WARNING\".*?inline=False\s*\))(.*?)(# Add the theta decay field.*?theta_decay_warning.*?inline=False\s*\))",
         r"\1\2\5\4"),  # Move theta decay before risk warning
    ]
    
    # Apply all patterns
    for pattern, replacement in patterns:
        modified_content = re.sub(pattern, replacement, modified_content, flags=re.DOTALL)
    
    # Final cleaning pattern to ensure we don't have double risk warnings
    # If we find "Add Risk Warning" followed by another "Add Risk Warning" with no theta decay in between,
    # remove the first one
    double_warning_pattern = r"(# Add Risk Warning.*?embed\.add_field\(\s*name=\"⚠️ RISK WARNING\".*?inline=False\s*\))(.*?)(# Add Risk Warning.*?embed\.add_field\(\s*name=\"⚠️ RISK WARNING\".*?inline=False\s*\))"
    modified_content = re.sub(double_warning_pattern, r"\2\3", modified_content, flags=re.DOTALL)
    
    # Special approach for the most reliable fix:
    # 1. Find all "return embed" statements
    # 2. Right before each one, ensure risk warning is the last field added
    
    return_embed_pattern = r"(\s+)return embed"
    
    def add_risk_warning_before_return(match):
        indent = match.group(1)
        # Add code to ensure risk warning is the last field
        return f"{indent}# Ensure risk warning is the very last field\n{indent}# First remove any existing risk warning field\n{indent}embed.fields = [field for field in embed.fields if '⚠️ RISK WARNING' not in field.name]\n{indent}# Then add it back at the end\n{indent}embed.add_field(\n{indent}    name=\"⚠️ RISK WARNING\",\n{indent}    value=\"Stop losses do not guarantee execution at the specified price in fast-moving markets.\",\n{indent}    inline=False\n{indent})\n{indent}return embed"
    
    modified_content = re.sub(return_embed_pattern, add_risk_warning_before_return, modified_content)
    
    # Write the updated content back to the file
    with open("discord_bot.py", "w") as file:
        file.write(modified_content)
    
    print("✅ Updated discord_bot.py to ensure risk warning is always the last field in the embed")

if __name__ == "__main__":
    fix_risk_warning_placement()