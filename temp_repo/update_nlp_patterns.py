"""
Update the NLP patterns in the Discord bot to improve ticker recognition
"""

import re

def update_nlp_patterns():
    """
    Update the NLP patterns in the Discord bot
    """
    try:
        with open('discord_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the extract_info method
        extract_info_method = re.search(r'def extract_info\(self, text\):(.*?)def parse_relative_dates', 
                                      content, re.DOTALL)
        
        if extract_info_method:
            current_method = extract_info_method.group(1)
            
            # Update the ticker pattern to better match tickers
            ticker_pattern = r"ticker_pattern = r'\\b([A-Z]{1,5})\\b'"
            ticker_new = "ticker_pattern = r'(?:\\bfor\\s+)?(?:\\bmy\\s+)?([A-Z]{1,5})\\b'"
            
            # Update the common words list
            common_words_pattern = r"common_words = \['WHAT', 'WILL', 'THE', 'FOR', 'ARE', 'OPTIONS', 'OPTION', 'CALLS?', 'PUTS?', 'STRIKE', 'PRICE', 'BE', 'WORTH', 'HOW', 'MUCH', 'CAN', 'YOU', 'TELL', 'ME', 'ABOUT', 'PREDICT', 'CALCULATE', 'ESTIMATE', 'SHOW', 'GET', 'BUY', 'SELL', 'CALL', 'PUT', 'AND', 'WITH', 'ANALYZE', 'UNUSUAL', 'ACTIVITY', 'STOP', 'LOSS'\]"
            common_words_new = "common_words = ['WHAT', 'WILL', 'THE', 'FOR', 'ARE', 'OPTIONS', 'OPTION', 'CALLS?', 'PUTS?', 'STRIKE', 'PRICE', 'BE', 'WORTH', 'HOW', 'MUCH', 'CAN', 'YOU', 'TELL', 'ME', 'ABOUT', 'PREDICT', 'CALCULATE', 'ESTIMATE', 'SHOW', 'GET', 'BUY', 'SELL', 'CALL', 'PUT', 'AND', 'WITH', 'ANALYZE', 'UNUSUAL', 'ACTIVITY', 'STOP', 'LOSS', 'RECOMMEND', 'GOOD', 'BAD', 'EXPIRING']"
            
            # Update the expiration pattern for better date matching
            expiration_pattern = r"expiration_pattern = r'(?:(?:expir(?:ing|e|es|ation)?\\s+(?:on|at|in)?\\s+)?(\\d{4}-\\d{2}-\\d{2}|\\w+\\s+\\d{1,2}(?:st|nd|rd|th)?\\s+\\d{4}|\\w+\\s+\\d{1,2}(?:st|nd|rd|th)?|\\d{1,2}(?:st|nd|rd|th)?\\s+\\w+\\s+\\d{4}|\\d{1,2}(?:st|nd|rd|th)?\\s+\\w+))'"
            expiration_new = "expiration_pattern = r'(?:(?:expir(?:ing|e|es|ation)?\\s+(?:on|at|in)?\\s+)?(\\d{4}-\\d{2}-\\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2}(?:st|nd|rd|th)?\\s+\\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2}(?:st|nd|rd|th)?|\\d{1,2}(?:st|nd|rd|th)?\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{4}|\\d{1,2}(?:st|nd|rd|th)?\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)))'"
            
            # Update the method
            updated_method = current_method
            if ticker_pattern in updated_method:
                updated_method = updated_method.replace(ticker_pattern, ticker_new)
            
            if common_words_pattern in updated_method:
                updated_method = updated_method.replace(common_words_pattern, common_words_new)
                
            if expiration_pattern in updated_method:
                updated_method = updated_method.replace(expiration_pattern, expiration_new)
            
            # Fix the strike price handling for dollar signs
            strike_handling_pattern = r"if match:\s+strike = match\.group\(1\) or match\.group\(2\)"
            strike_handling_new = '''if match:
            strike_str = match.group(1) or match.group(2)
            # Clean up dollar signs if present
            if strike_str and "$" in strike_str:
                strike_str = strike_str.replace("$", "")
            strike = float(strike_str) if strike_str else None'''
            
            if re.search(strike_handling_pattern, updated_method):
                updated_method = re.sub(strike_handling_pattern, strike_handling_new, updated_method)
            
            # Update the content
            content = content.replace(extract_info_method.group(1), updated_method)
        
        # Write the updated content
        with open('discord_bot.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Successfully updated NLP patterns in discord_bot.py")
    except Exception as e:
        print(f"Error updating NLP patterns: {str(e)}")

if __name__ == "__main__":
    update_nlp_patterns()