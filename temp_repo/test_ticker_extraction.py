"""
A focused test script that verifies the new ticker extraction logic in discord_bot.py
"""

import re
import os

def test_ticker_extraction():
    print("Testing ticker extraction patterns")
    print("=================================")
    
    # Define test cases and expected results
    test_cases = [
        ("What's a good stop loss for AAPL $190 calls?", "AAPL"),
        ("Recommend stop loss for TSLA $270 calls expiring Apr 4th", "TSLA"),
        ("Can you tell me about my MSFT $400 puts expiring next Friday?", "MSFT"),
        ("I need help with AMD 120 calls", "AMD"),
        ("Stop loss for my NVDA 500 calls please", "NVDA"),
        ("What will SPY 470 puts be worth if market drops 2%?", "SPY"),
        ("Show unusual activity for AMZN", "AMZN")
    ]
    
    # Common words to exclude
    common_words = ['WHAT', 'WILL', 'THE', 'FOR', 'ARE', 'OPTIONS', 'OPTION', 'CALL', 'PUT', 
                   'STRIKE', 'PRICE', 'BE', 'WORTH', 'HOW', 'MUCH', 'CAN', 'YOU', 'TELL', 
                   'ME', 'ABOUT', 'PREDICT', 'CALCULATE', 'ESTIMATE', 'SHOW', 'GET', 'BUY', 
                   'SELL', 'AND', 'WITH', 'ANALYZE', 'UNUSUAL', 'ACTIVITY', 'STOP', 'LOSS',
                   'RECOMMEND', 'GOOD', 'BAD', 'EXPIRING', 'NEXT', 'MY', 'PLEASE', 'HELP',
                   'NEED', 'IF']
    
    # Different patterns to test
    patterns = [
        (r'\b([A-Z]{1,5})\b', "Simple word boundary pattern"),
        (r'(?:\bfor\s+|\bmy\s+)?([A-Z]{1,5})\b', "Pattern with optional 'for' or 'my' prefix"),
        (r'(?:for|my)\s+([A-Z]{1,5})\b', "Pattern requiring 'for' or 'my' prefix")
    ]
    
    # Test each pattern
    for pattern_regex, pattern_desc in patterns:
        print(f"\n{pattern_desc}:")
        print("-" * len(pattern_desc))
        
        success = 0
        for query, expected in test_cases:
            query = query.upper()  # Convert to uppercase as the bot would
            
            # Find all potential tickers
            potential_tickers = []
            
            if "for|my" in pattern_regex:
                # This pattern directly extracts the ticker after for/my
                matches = re.findall(pattern_regex, query)
                potential_tickers = matches
            else:
                # Standard pattern that returns all potential matches
                matches = re.findall(pattern_regex, query)
                # Filter out common words
                potential_tickers = [m for m in matches if m not in common_words]
            
            # Get the first non-common word as the ticker
            extracted_ticker = potential_tickers[0] if potential_tickers else None
            
            result = "✅ PASS" if extracted_ticker == expected else f"❌ FAIL (got {extracted_ticker})"
            print(f"Query: {query}")
            print(f"Expected: {expected}, Extracted: {extracted_ticker}")
            print(f"Result: {result}")
            print()
            
            if extracted_ticker == expected:
                success += 1
        
        print(f"Pattern success rate: {success}/{len(test_cases)} ({success/len(test_cases)*100:.1f}%)")
    
    # Test the enhanced algorithm that combines both approaches
    print("\nEnhanced algorithm (check for ticker after specific words if standard approach fails):")
    print("-" * 80)
    
    success = 0
    for query, expected in test_cases:
        query = query.upper()  # Convert to uppercase as the bot would
        
        # First try standard approach
        standard_pattern = r'\b([A-Z]{1,5})\b'
        matches = re.findall(standard_pattern, query)
        filtered_matches = [m for m in matches if m not in common_words]
        extracted_ticker = filtered_matches[0] if filtered_matches else None
        
        # If standard approach fails, try looking for ticker after specific words
        if not extracted_ticker:
            specific_pattern = r'(?:FOR|MY)\s+([A-Z]{1,5})\b'
            match = re.search(specific_pattern, query)
            if match:
                potential_ticker = match.group(1)
                if potential_ticker not in common_words:
                    extracted_ticker = potential_ticker
        
        result = "✅ PASS" if extracted_ticker == expected else f"❌ FAIL (got {extracted_ticker})"
        print(f"Query: {query}")
        print(f"Expected: {expected}, Extracted: {extracted_ticker}")
        print(f"Result: {result}")
        print()
        
        if extracted_ticker == expected:
            success += 1
    
    print(f"Enhanced algorithm success rate: {success}/{len(test_cases)} ({success/len(test_cases)*100:.1f}%)")

if __name__ == "__main__":
    test_ticker_extraction()