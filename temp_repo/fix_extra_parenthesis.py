"""
This script fixes the extra closing parenthesis in the discord_bot.py file.
"""

def fix_extra_parenthesis():
    """
    Find and remove the extra closing parenthesis on line 2027.
    """
    with open('discord_bot.py', 'r') as file:
        lines = file.readlines()
    
    # Fix the line with the extra closing parenthesis
    line_number = 2026
    while line_number < len(lines):
        # Look for the extra ) that appears right after the embed.add_field block
        if '))' in lines[line_number] and 'inline=False' not in lines[line_number]:
            # Replace the double parenthesis with a single one
            lines[line_number] = lines[line_number].replace('))', ')')
        # Also check for standalone ) on a line by itself with indentation
        if lines[line_number].strip() == ')':
            # Remove the line completely
            lines[line_number] = ''
        line_number += 1
    
    # Write the fixed content back to the file
    with open('discord_bot.py', 'w') as file:
        file.writelines(lines)
    
    print("Fixed the extra closing parenthesis in discord_bot.py")

if __name__ == "__main__":
    fix_extra_parenthesis()