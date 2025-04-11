"""
This script modifies the handle_stop_loss_request method to ensure that the risk warning
is always added as the very last field in the embed, after any theta decay projections.
"""

def fix_risk_placement():
    """
    Directly modify the handle_stop_loss_request method to ensure proper field order
    """
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    # Find all occurrences of risk warning being added
    # The pattern is something like:
    # embed.add_field(
    #     name="⚠️ RISK WARNING",
    #     value="Stop losses do not guarantee execution...",
    #     inline=False
    # )
    
    import re
    
    # Remove all existing risk warning additions
    risk_warning_pattern = r"# Add Risk Warning.*?embed\.add_field\(\s*name=\"⚠️ RISK WARNING\".*?inline=False\s*\)"
    content_without_risk = re.sub(risk_warning_pattern, "# Risk warning will be added at the end", content, flags=re.DOTALL)
    
    # Find all return embed statements and add the risk warning right before them
    return_pattern = r"(\s+)return embed"
    
    def add_risk_warning(match):
        indent = match.group(1)
        return f"{indent}# Add Risk Warning at the very end\n{indent}embed.add_field(\n{indent}    name=\"⚠️ RISK WARNING\",\n{indent}    value=\"Stop losses do not guarantee execution at the specified price in fast-moving markets.\",\n{indent}    inline=False\n{indent})\n{indent}return embed"
    
    fixed_content = re.sub(return_pattern, add_risk_warning, content_without_risk)
    
    # Write the updated content back to the file
    with open("discord_bot.py", "w") as file:
        file.write(fixed_content)
    
    print("✅ Fixed risk warning placement to ensure it appears as the last field")

if __name__ == "__main__":
    fix_risk_placement()