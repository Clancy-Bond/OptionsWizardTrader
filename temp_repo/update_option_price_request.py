"""
Update the handle_option_price_request method in the Discord bot to use the new expiration date validation
"""

import re

def update_option_price_request():
    """
    Update the handle_option_price_request method in discord_bot.py
    """
    try:
        with open('discord_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find handle_option_price_request method
        price_method = re.search(r'async def handle_option_price_request\(self, message, info\):(.*?)(?=async def|$)', 
                               content, re.DOTALL)
        
        if price_method:
            current_method = price_method.group(0)
            
            # Add better validation for required fields
            validation_pattern = r'if not all\(\[ticker, option_type, strike_price\]\):'
            validation_new = '''if not ticker:
            return await message.channel.send("Please provide a valid ticker symbol.")
        
        if not option_type:
            return await message.channel.send("Please specify whether you are looking for calls or puts.")
        
        if not strike_price:
            return await message.channel.send("Please provide a strike price for your option position.")'''
            
            # Add + sign for profits
            profit_pattern = r'total_profit = estimated_price \* 100 \* num_contracts - current_value'
            profit_new = '''total_profit = estimated_price * 100 * num_contracts - current_value
                
                # Format profit/loss with + or - sign
                profit_prefix = "+" if total_profit > 0 else ""'''
            
            profit_display_pattern = r'"Estimated Total P/L": \${total_profit:.2f}'
            profit_display_new = '"Estimated Total P/L": {profit_prefix}${total_profit:.2f}'
            
            # Make the replacements if patterns are found
            updated_method = current_method
            if re.search(validation_pattern, updated_method):
                updated_method = re.sub(validation_pattern, validation_new, updated_method)
            
            if re.search(profit_pattern, updated_method):
                updated_method = re.sub(profit_pattern, profit_new, updated_method)
                
            if profit_display_pattern in updated_method:
                updated_method = updated_method.replace(profit_display_pattern, profit_display_new)
            
            # Update the content
            content = content.replace(current_method, updated_method)
        
        # Write the updated content
        with open('discord_bot.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Successfully updated handle_option_price_request in discord_bot.py")
    except Exception as e:
        print(f"Error updating handle_option_price_request: {str(e)}")

if __name__ == "__main__":
    update_option_price_request()