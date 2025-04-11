"""
This script improves the regex patterns in discord_bot.py to better handle various formats of queries,
especially those with dollar signs in strike prices and dates with ordinal suffixes.
"""

import re

def update_discord_bot_patterns():
    """
    Update the regex patterns in discord_bot.py
    """
    try:
        with open('discord_bot.py', 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Find the OptionsBotNLP class and the extract_info method
        pattern_section = re.search(r'def extract_info\(self, text\):(.+?)def parse_relative_dates', 
                                   content, re.DOTALL)
        
        if not pattern_section:
            print("Could not find the extract_info method in discord_bot.py")
            return
            
        # Get the current patterns section
        current_patterns = pattern_section.group(1)
        
        # Define the improved patterns
        ticker_pattern = r'ticker_pattern = r\'\\b([A-Z]{1,5})\\b\''
        new_ticker_pattern = r'ticker_pattern = r\'(?:\\bfor\\s+|\\bmy\\s+)?([A-Z]{1,5})\\b\''
        
        strike_pattern = r'strike_pattern = r\'(?:\$?(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s?(?:strike|[$]))\''
        new_strike_pattern = r'strike_pattern = r\'(?:\$?(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s?(?:strike|[$]))\''
        
        expiration_pattern = r'expiration_pattern = r\'(?:(?:expir(?:ing|e|es|ation)?\s+(?:on|at|in)?\s+)?(\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4}|\w+\s+\d{1,2}(?:st|nd|rd|th)?|\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|\d{1,2}(?:st|nd|rd|th)?\s+\w+))\''
        new_expiration_pattern = r'expiration_pattern = r\'(?:(?:expir(?:ing|e|es|ation)?\s+(?:on|at|in)?\s+)?(\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)))\''
        
        # Replace the patterns
        updated_patterns = current_patterns
        updated_patterns = re.sub(ticker_pattern, new_ticker_pattern, updated_patterns)
        updated_patterns = re.sub(strike_pattern, new_strike_pattern, updated_patterns)
        updated_patterns = re.sub(expiration_pattern, new_expiration_pattern, updated_patterns)
        
        # Update the content
        updated_content = content.replace(current_patterns, updated_patterns)
        
        # Fix the strike price handling in case it's a string with '$'
        strike_handling_pattern = r'strike = match\.group\(1\) or match\.group\(2\)'
        new_strike_handling = r'strike_str = match.group(1) or match.group(2)\n            # Clean up dollar signs if present\n            if strike_str and "$" in strike_str:\n                strike_str = strike_str.replace("$", "")\n            strike = float(strike_str) if strike_str else None'
        
        updated_content = re.sub(strike_handling_pattern, new_strike_handling, updated_content)
        
        # Also fix the strike price is None check in handle_stop_loss_request and handle_option_price_request
        for method in ["handle_stop_loss_request", "handle_option_price_request"]:
            method_pattern = f"def {method}\\(self, message, info\\):(.+?)(?:def |$)"
            method_match = re.search(method_pattern, updated_content, re.DOTALL)
            
            if method_match:
                method_content = method_match.group(1)
                
                # Add better error handling for missing strike prices
                strike_check = "if not all\\(\\[ticker, option_type, strike_price\\]\\):"
                strike_check_replacement = "if not ticker:\n            return await message.channel.send(\"Please provide a valid ticker symbol.\")\n        \n        if not option_type:\n            return await message.channel.send(\"Please specify whether you are looking for calls or puts.\")\n        \n        if not strike_price:\n            return await message.channel.send(\"Please provide a strike price for your option position.\")"
                
                method_content = re.sub(strike_check, strike_check_replacement, method_content)
                updated_content = updated_content.replace(method_match.group(1), method_content)
        
        # Add better error handling for the options chain retrieval
        options_chain_pattern = r'try:\s+option_chain = get_option_chain\(ticker_data, expiration_date, option_type\)\s+except Exception as e:\s+print\(f"Error getting option chain: {str\(e\)}"\)\s+option_chain = None'
        options_chain_replacement = '''try:
                # First check if the expiration date is available
                available_expirations = ticker_data.options
                
                if not available_expirations:
                    return await message.channel.send(f"No options data available for {ticker}. The market may be closed or this stock might not have options trading.")
                    
                if expiration_date not in available_expirations:
                    # Find closest available expiration
                    expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d').date()
                    closest_date = min(available_expirations, key=lambda x: abs((datetime.strptime(x, '%Y-%m-%d').date() - expiration_date_obj).days))
                    
                    await message.channel.send(f"⚠️ Expiration date {expiration_date} not found for {ticker}. Using closest available expiration: {closest_date}.")
                    expiration_date = closest_date
                
                # Get option chain for the specific expiration
                option_chain = get_option_chain(ticker_data, expiration_date, option_type)
                if option_chain is None or option_chain.empty:
                    return await message.channel.send(f"No option chain available for {ticker} {option_type} expiring {expiration_date}. Please check that this option exists.")
            except Exception as e:
                print(f"Error getting option chain: {str(e)}")
                await message.channel.send(f"⚠️ Could not retrieve options data for {ticker} expiring {expiration_date}. This might be due to market hours or data availability issues.")
                option_chain = None'''
        
        updated_content = re.sub(options_chain_pattern, options_chain_replacement, updated_content)
        
        # Write the updated content back to the file
        with open('discord_bot.py', 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        print("Successfully updated discord_bot.py with improved regex patterns")
    except Exception as e:
        print(f"Error updating discord_bot.py: {str(e)}")

if __name__ == "__main__":
    update_discord_bot_patterns()