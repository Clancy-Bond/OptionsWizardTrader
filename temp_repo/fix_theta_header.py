"""
This script fixes the redundancy in theta decay projection displays by:
1. Modifying option_calculator.py to not include the header in the warning_message
2. Updating discord_bot.py to use f-strings for the field name with the date
"""

import re

def fix_option_calculator():
    """Fix the warning_message creation in calculate_expiry_theta_decay"""
    try:
        with open('option_calculator.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the line that creates the warning message header
        # warning_message = f"⚠️ **THETA DECAY PROJECTION TO EXPIRY ({expiration_date})** ⚠️\n"
        # We want to remove this line so it doesn't appear in the field content
        
        # Match the pattern and remove the line
        pattern = r'warning_message = f"⚠️ \*\*THETA DECAY PROJECTION TO EXPIRY \({expiration_date}\)\*\* ⚠️\\n"'
        replacement = 'warning_message = ""'
        
        modified_content = re.sub(pattern, replacement, content)
        
        with open('option_calculator.py', 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print("✅ Successfully modified option_calculator.py")
        
    except Exception as e:
        print(f"❌ Error modifying option_calculator.py: {e}")

def fix_discord_bot():
    """Update discord_bot.py to include the date in the field name"""
    try:
        with open('discord_bot.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find all instances where the theta decay field is added
        # Example: name="⚠️ THETA DECAY PROJECTION ⚠️",
        # We want to change it to: name=f"⚠️ THETA DECAY PROJECTION TO ({expiration_date}) ⚠️",
        
        # Replace all instances
        instances = [
            # Pattern for theta decay field in handle_option_price_request
            (r'name="⚠️ THETA DECAY PROJECTION ⚠️"', 
             r'name=f"⚠️ THETA DECAY PROJECTION TO ({info["expiration"]}) ⚠️"'),
            
            # Pattern for theta decay field in handle_stop_loss_request
            (r'name="⚠️ THETA DECAY PROJECTION ⚠️"', 
             r'name=f"⚠️ THETA DECAY PROJECTION TO ({info["expiration"]}) ⚠️"')
        ]
        
        modified_content = content
        for pattern, replacement in instances:
            modified_content = modified_content.replace(pattern, replacement)
        
        with open('discord_bot.py', 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print("✅ Successfully modified discord_bot.py")
        
    except Exception as e:
        print(f"❌ Error modifying discord_bot.py: {e}")

if __name__ == "__main__":
    fix_option_calculator()
    fix_discord_bot()