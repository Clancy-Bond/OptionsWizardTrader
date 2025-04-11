"""
This script adds improved error handling to the Discord bot,
specifically for the case where market data isn't available for a future date.
"""

import re

def main():
    """
    Update error handling in the discord_bot.py file
    """
    # Read the discord_bot.py file
    try:
        with open('discord_bot.py', 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading discord_bot.py: {str(e)}")
        return
    
    # Pattern to find the generic error message
    generic_error_pattern = re.compile(
        r'await message\.channel\.send\(f"Sorry, I encountered an error processing your request\. '
        r'Please try again with more specific details\\\.\\n\\nTry asking about:'
    )
    
    # Replace with more specific error message for issues with options data
    improved_message = (
        'error_message = f"Sorry, I encountered an error processing your request for {ticker} ${strike_price} {option_type}"\n'
        '            if expiration_date:\n'
        '                error_message += f" expiring {expiration_date}"\n'
        '            error_message += ".\\n\\n"\n'
        '            \n'
        '            # Add specific guidance based on the error\n'
        '            if "Invalid ticker" in str(e) or "not found" in str(e).lower():\n'
        '                error_message += f"⚠️ Could not find ticker \'{ticker}\'. Please verify the stock symbol is correct."\n'
        '            elif "expiration" in str(e).lower():\n'
        '                error_message += f"⚠️ Issue with expiration date \'{expiration_date}\'. The options chain for this date may not be available."\n'
        '            elif "No options" in str(e):\n'
        '                error_message += f"⚠️ No options data available for {ticker} expiring {expiration_date}. This may be because:\\n"\n'
        '                error_message += "• The market is currently closed\\n"\n'
        '                error_message += "• This option doesn\'t exist or isn\'t actively traded\\n"\n'
        '                error_message += "• The expiration date may be too far in the future"\n'
        '            else:\n'
        '                error_message += "Please try again with more specific details.\\n\\nTry asking about:\\n• Option price estimates (e.g., AAPL $190 calls expiring next month)\\n• Stop loss recommendations (e.g., stop loss for MSFT puts)\\n• Unusual options activity for a ticker"\n'
        '            \n'
        '            await message.channel.send(error_message)'
    )
    
    # Do the replacement
    modified_content = generic_error_pattern.sub(improved_message, content)
    
    # Count replacements
    replacement_count = len(re.findall(r'⚠️ Could not find ticker', modified_content))
    
    # Write the modified content back to the file
    try:
        with open('discord_bot.py', 'w', encoding='utf-8') as file:
            file.write(modified_content)
        print(f"Successfully updated discord_bot.py with improved error handling. Made {replacement_count} replacements.")
    except Exception as e:
        print(f"Error writing to discord_bot.py: {str(e)}")

if __name__ == "__main__":
    main()