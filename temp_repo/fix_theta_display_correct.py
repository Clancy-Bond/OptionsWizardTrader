"""
This script fixes the syntax error in the discord_bot.py file where f-strings are improperly
formatted with nested double quotes.
"""

import re

def fix_discord_bot():
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Find all occurrences of the problematic f-string format
    pattern = r'name=f"⚠️ THETA DECAY PROJECTION TO \(\{info\["expiration"\]\}\) ⚠️",'
    replacement = r'name=f"⚠️ THETA DECAY PROJECTION TO ({info[\'expiration\']}) ⚠️",'
    
    if pattern in content:
        modified_content = content.replace(pattern, replacement)
    else:
        # Direct find and replace for the specific instances we know about
        instances = [
            (r'name=f"⚠️ THETA DECAY PROJECTION TO ({info["expiration"]}) ⚠️",', 
             r'name=f"⚠️ THETA DECAY PROJECTION TO ({info[\'expiration\']}) ⚠️",')
        ]
        
        modified_content = content
        for old, new in instances:
            modified_content = modified_content.replace(old, new)
    
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(modified_content)

# Fix the option_calculator.py file as well
def fix_option_calculator():
    with open('option_calculator.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove the projection header line from the warning message
    warning_message_pattern = r'warning_message = f"⚠️ \*\*THETA DECAY PROJECTION TO EXPIRY \({expiration_date}\)\*\* ⚠️\\n"'
    warning_message_replacement = r'warning_message = ""'
    
    modified_content = content.replace(warning_message_pattern, warning_message_replacement)
    
    with open('option_calculator.py', 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("✅ Successfully updated option_calculator.py")

if __name__ == "__main__":
    print("Starting fixes...")
    fix_option_calculator()
    fix_discord_bot()
    print("✅ Successfully updated discord_bot.py")
    print("All fixes complete!")