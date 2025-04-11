"""
Final update to the ticker extraction and pattern matching in Discord bot
"""

import re

def update_nlp_extraction():
    try:
        with open('discord_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find the extract_info method
        extract_info_method = re.search(r'def extract_info\(self, text\):(.*?)def parse_relative_dates', 
                                      content, re.DOTALL)
        
        if not extract_info_method:
            print("Could not find the extract_info method in discord_bot.py")
            return
            
        current_method = extract_info_method.group(1)
        
        # Replace the ticker extraction logic with improved logic
        ticker_extraction_pattern = r"# Extract ticker symbol \(1-5 uppercase letters\).*?for match in ticker_matches:.*?break"
        ticker_extraction_new = '''# Extract ticker symbol (1-5 uppercase letters)
        ticker_pattern = r'\\b([A-Z]{1,5})\\b'
        ticker_matches = re.findall(ticker_pattern, text)
        
        for match in ticker_matches:
            if match not in self.common_words:
                info['ticker'] = match
                break
                
        # If we couldn't find a ticker that way, try to find tickers after specific words
        if not info['ticker']:
            # Look for tickers after common prepositions
            for prefix in ['FOR', 'MY', 'WITH', 'ON', 'IN']:
                ticker_after_word = re.search(prefix + r'\\s+([A-Z]{1,5})\\b', text)
                if ticker_after_word:
                    potential_ticker = ticker_after_word.group(1)
                    if potential_ticker not in self.common_words:
                        info['ticker'] = potential_ticker
                        break
                        
        # Special case for known stock tickers that might be mentioned in queries
        if not info['ticker']:
            for known_ticker in ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'SPY', 'QQQ', 'IWM']:
                if known_ticker in text:
                    info['ticker'] = known_ticker
                    break'''
                
        updated_method = re.sub(ticker_extraction_pattern, ticker_extraction_new, current_method, flags=re.DOTALL)
        
        # Fix the strike price handling for dollar signs
        strike_handling_pattern = r"if match:\s+strike = match\.group\(1\) or match\.group\(2\)"
        strike_handling_new = '''if match:
            strike_str = match.group(1) or match.group(2)
            # Clean up dollar signs if present
            if strike_str and "$" in strike_str:
                strike_str = strike_str.replace("$", "")
            strike = float(strike_str) if strike_str else None'''
        
        updated_method = re.sub(strike_handling_pattern, strike_handling_new, updated_method, flags=re.DOTALL)
        
        # Update the content
        updated_content = content.replace(extract_info_method.group(1), updated_method)
        
        # Write the updated content
        with open('discord_bot.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        print("Successfully updated ticker pattern extraction in discord_bot.py")
    except Exception as e:
        print(f"Error updating ticker pattern extraction: {str(e)}")

if __name__ == "__main__":
    update_nlp_extraction()