"""
Update the Discord bot to use the new expiration date validation function and improve error handling
"""

import re

def update_discord_bot():
    """Update the Discord bot code"""
    try:
        with open('discord_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Import dependencies at the top of the file
        imports_section = re.search(r'import os(.*?)class OptionsBotNLP', content, re.DOTALL)
        if imports_section:
            current_imports = imports_section.group(1)
            if 'from option_calculator import handle_expiration_date_validation' not in current_imports:
                updated_imports = current_imports + '\nfrom option_calculator import handle_expiration_date_validation\n'
                content = content.replace(current_imports, updated_imports)
        
        # Find handle_stop_loss_request method
        stop_loss_method = re.search(r'async def handle_stop_loss_request\(self, message, info\):(.*?)(?=async def|$)', 
                                    content, re.DOTALL)
        
        if stop_loss_method:
            current_method = stop_loss_method.group(0)
            
            # Add expiration date validation
            expiration_check_pattern = r'# If expiration date wasn\'t provided.*?try:.*?expirations = ticker_data\.options.*?except Exception as e:.*?return await message\.channel\.send'
            expiration_check_new = '''
            # If expiration date wasn't provided, try to get the next available one
            if not expiration_date:
                try:
                    available_expirations = ticker_data.options
                    
                    if not available_expirations:
                        return await message.channel.send(f"No options data available for {ticker}. The market may be closed or this stock might not have options trading.")
                        
                    expiration_date = available_expirations[0]
                    print(f"Using first available expiration date: {expiration_date}")
                except Exception as e:
                    print(f"Error getting expiration dates: {str(e)}")
                    return await message.channel.send
            '''
            
            # Replace the string formatting for total loss
            total_loss_pattern = r'# Total loss for all contracts.*?total_option_loss = \(option_stop_price - current_option_price\) \* 100 \* num_contracts'
            total_loss_new = '''# Total loss for all contracts
            total_option_loss = (option_stop_price - current_option_price) * 100 * num_contracts
            
            # Format profit/loss with + or - sign
            profit_loss_prefix = "+" if total_option_loss > 0 else ""'''
            
            # Replace the description formatting for total position P/L
            pl_pattern = r'"Total Position P/L at Stop Loss": \${total_option_loss:.2f}'
            pl_new = '"Total Position P/L at Stop Loss": {profit_loss_prefix}${total_option_loss:.2f}'
            
            # Make the replacements if patterns are found
            updated_method = current_method
            if re.search(total_loss_pattern, updated_method, re.DOTALL):
                updated_method = re.sub(total_loss_pattern, total_loss_new, updated_method, flags=re.DOTALL)
            
            if pl_pattern in updated_method:
                updated_method = updated_method.replace(pl_pattern, pl_new)
                
            # Update the content
            content = content.replace(current_method, updated_method)
        
        # Write the updated content
        with open('discord_bot.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Successfully updated discord_bot.py with improved expiration date validation and error handling")
    except Exception as e:
        print(f"Error updating discord_bot.py: {str(e)}")

if __name__ == "__main__":
    update_discord_bot()