"""
Fix all missing parentheses in add_field calls throughout discord_bot.py
"""

import re

def fix_add_field_parentheses():
    """
    Find all add_field calls that don't end with a closing parenthesis and fix them
    """
    # Read the file
    with open('discord_bot.py', 'r') as f:
        content = f.read()
    
    # Pattern to find add_field calls that have multiple parameters and don't end with )
    pattern = r'(embed\.add_field\(\s*name=["\'][^"\']*["\'],\s*value=["\'][^"\']*["\'],\s*inline=(True|False))\s*(?!\))'
    
    # Replace with the same content plus a closing parenthesis
    fixed_content = re.sub(pattern, r'\1)', content)
    
    # Write the fixed content back to the file
    with open('discord_bot.py', 'w') as f:
        f.write(fixed_content)
    
    # Check how many fixes were made
    original_matches = len(re.findall(pattern, content))
    print(f"Fixed {original_matches} add_field calls missing closing parentheses")

if __name__ == "__main__":
    fix_add_field_parentheses()