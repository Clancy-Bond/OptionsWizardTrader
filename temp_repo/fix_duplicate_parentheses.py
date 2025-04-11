"""
Fix all double parentheses in discord_bot.py
"""

import re

def fix_duplicate_parentheses():
    """Fix double parentheses that resulted from our previous fixes"""
    with open('discord_bot.py', 'r') as f:
        content = f.read()
    
    # Find all instances of '))' that are not preceded by '(' to avoid nested parentheses
    pattern = r'(?<!\()\)\)'
    
    # Replace with single closing parenthesis
    fixed_content = re.sub(pattern, ')', content)
    
    # Now handle the specific pattern we're seeing in the file:
    # Look for add_field calls with extra parentheses at the end
    pattern2 = r'inline=False\) \)'
    fixed_content = re.sub(pattern2, 'inline=False)', fixed_content)
    
    # Also try with True
    pattern3 = r'inline=True\) \)'
    fixed_content = re.sub(pattern3, 'inline=True)', fixed_content)
    
    # Handle patterns where there might be a space between parentheses
    pattern4 = r'\) \)'
    fixed_content = re.sub(pattern4, ')', fixed_content)
    
    # Write the fixed content back to the file
    with open('discord_bot.py', 'w') as f:
        f.write(fixed_content)
    
    # Count the number of replacements for all patterns
    original_count1 = len(re.findall(pattern, content))
    original_count2 = len(re.findall(pattern2, content))
    original_count3 = len(re.findall(pattern3, content))
    original_count4 = len(re.findall(pattern4, content))
    total_count = original_count1 + original_count2 + original_count3 + original_count4
    
    print(f"Fixed {total_count} instances of duplicate parentheses:"
          f"\n  - {original_count1} instances of '))',"
          f"\n  - {original_count2} instances of 'inline=False) )',"
          f"\n  - {original_count3} instances of 'inline=True) )',"
          f"\n  - {original_count4} instances of ') )'.")

if __name__ == "__main__":
    fix_duplicate_parentheses()