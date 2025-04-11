"""
Fixes the expiration date handling in handle_stop_loss_request.
"""

import re

def fix_expiration_handling():
    """
    Update the handle_stop_loss_request method to handle missing expiration date
    by providing a default or asking the user for it.
    """
    with open('discord_bot.py', 'r') as file:
        content = file.read()

    # Find the handle_stop_loss_request method
    pattern = r'(async def handle_stop_loss_request\(self, message, info\):.*?)(?=\s+async def)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        method = match.group(1)
        
        # Add check and default for missing expiration
        modified_method = method.replace(
            'print(f"DEBUG: Getting stop loss recommendations with expiration: {info[\'expiration\']}")',
            '# Set default expiration date if not provided\n'
            '        if \'expiration\' not in info:\n'
            '            from datetime import datetime, timedelta\n'
            '            # Default to next Friday if no expiration is provided\n'
            '            today = datetime.now()\n'
            '            days_until_friday = (4 - today.weekday()) % 7\n'
            '            if days_until_friday == 0:  # If today is Friday, get next Friday\n'
            '                days_until_friday = 7\n'
            '            next_friday = today + timedelta(days=days_until_friday)\n'
            '            info[\'expiration\'] = next_friday.strftime(\'%Y-%m-%d\')\n'
            '            print(f"DEBUG: No expiration date provided, using default: {info[\'expiration\']}")\n'
            '        else:\n'
            '            print(f"DEBUG: Using provided expiration: {info[\'expiration\']}")'
        )
        
        updated_content = content.replace(method, modified_method)
        
        with open('discord_bot.py', 'w') as file:
            file.write(updated_content)
        
        print("Successfully updated handle_stop_loss_request method to handle missing expiration dates!")
    else:
        print("Could not find the handle_stop_loss_request method in discord_bot.py")

if __name__ == "__main__":
    fix_expiration_handling()