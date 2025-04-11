"""
A comprehensive fix for all the remaining syntax issues in discord_bot.py.
This script uses regular expressions to search and fix multiple syntax issues:

1. Fix for parentheses pattern on line 1088-1089
2. Fix for any other similar min() function calls with missing closing parentheses
3. Fix for any patterns in regex syntax that have unbalanced parentheses
"""

import re

def fix_all_remaining_issues():
    """Identify and fix all remaining syntax issues in discord_bot.py"""
    with open('discord_bot.py', 'r') as f:
        content = f.read()
    
    # Fix the min() function call pattern
    min_pattern = r'min\(range\(len\([^)]+\)\),\s*\n\s*key=lambda [^:]+:[^)]+\)'
    min_replacement = lambda match: match.group().replace('\n', ' ')
    fixed_content = re.sub(min_pattern, min_replacement, content)
    
    # Fix any regex patterns with unbalanced parentheses (line 66, 68, 490)
    patterns_to_check = [
        # line 66 'strike' pattern
        r"'strike': r'(?:\\\\$\\(\\d+\\.\\?\\d\\*\\)\\|\\(\\?:strike\\s\\+\\(\\?:price\\s\\+\\)\\?\\(\\?:of\\s\\+\\)\\?\\\\\\$\\?\\(\\d+\\.\\?\\d\\*\\)\\|\\(\\?:strike\\s\\+\\(\\?:price\\s\\+\\)\\?\\(\\?:at\\s\\+\\)\\?\\\\\\$\\?\\(\\d+\\.\\?\\d\\*\\)\\|\\(\\?:\\\\\\$\\(\\d+\\.\\?\\d\\*\\)\\s\\+\\(\\?:calls\\?\\|puts\\?\\)\\\\b\\)\\|\\(\\d+\\.\\?\\d\\*\\)\\s\\+\\(\\?:calls\\?\\|puts\\?\\)\\\\b'",
        # line 68 'move_amount' pattern
        r"'move_amount': r'(?:move(?:s|d)?\\s+(?:by|up|down)?\\s+\\\\$?(\\d+\\.?\\d*)|(?:up|down)\\s+\\\\$?(\\d+\\.?\\d*)|(?:reach|hits|go(?:es)? to|at)\\s+\\\\$?(\\d+\\.?\\d*)|(?:rise|drop)s?\\s+(?:by)?\\s+\\\\$?(\\d+\\.?\\d*)|\\\\$(\\d+\\.?\\d*)\\s+(?:higher|lower)|\\+\\\\$?(\\d+\\.?\\d*)|\\-\\\\$?(\\d+\\.?\\d*)'",
        # line 490 contract_count pattern
        r"have_contracts_match = re.search\\(r'I\\s\\+have\\s\\+(\\d+)(?:\\s\\+(?:[a-zA-Z\\\\$]+\\s\\+)*(?:contracts?|positions?|options?))?'",
    ]
    
    for pattern in patterns_to_check:
        # Find the pattern in the content
        match = re.search(pattern, fixed_content)
        if match:
            # Extract the pattern
            matched_text = match.group(0)
            # Check if it has an unequal number of opening and closing parentheses
            opening = matched_text.count('(')
            closing = matched_text.count(')')
            
            if opening > closing:
                # Add the missing closing parentheses
                fixed_text = matched_text + ")" * (opening - closing)
                fixed_content = fixed_content.replace(matched_text, fixed_text)
                print(f"Fixed pattern with {opening-closing} missing closing parentheses")
    
    # Write the fixed content back to the file
    with open('discord_bot.py', 'w') as f:
        f.write(fixed_content)
    
    print("Fixed all remaining issues in discord_bot.py")

if __name__ == "__main__":
    fix_all_remaining_issues()