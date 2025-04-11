"""
Test script to specifically test the stop-loss query format reported as problematic.
"""
import re
from datetime import datetime
from dateutil import parser

def test_stop_loss_query():
    """Test the stop-loss query format that was failing"""
    query = "Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    print(f"Testing query: '{query}'")
    
    # Extract ticker
    ticker_pattern = r'\b[A-Z]{1,5}\b'
    ticker_matches = re.findall(ticker_pattern, query)
    if ticker_matches:
        print(f"Found ticker(s): {ticker_matches}")
        ticker = next((t for t in ticker_matches if t in ["AAPL", "MSFT", "GOOG", "GOOGL", "AMZN", "META", "TSLA"]), ticker_matches[0])
        print(f"Selected ticker: {ticker}")
    else:
        print("No ticker found")
    
    # Extract strike price
    strike_pattern = r'(?:\$(\d+\.?\d*))|(?:strike\s+(?:price\s+)?(?:of\s+)?\$?(\d+\.?\d*))|(?:strike\s+(?:price\s+)?(?:at\s+)?\$?(\d+\.?\d*))|(?:\$(\d+\.?\d*)\s+(?:calls?|puts?)\b)|(?:\b(\d+\.?\d*)\s+(?:calls?|puts?)\b)'
    strike_match = re.search(strike_pattern, query)
    if strike_match:
        print(f"Strike match: {strike_match.group()}")
        # Get the first non-None group
        strike = next((g for g in strike_match.groups() if g is not None), None)
        if strike:
            print(f"Extracted strike price: {strike}")
    else:
        print("No strike price found")
    
    # Extract option type
    option_type_pattern = r'\b(call|put)s?\b'
    option_type_match = re.search(option_type_pattern, query.lower())
    if option_type_match:
        print(f"Option type match: {option_type_match.group()}")
        option_type = option_type_match.group(1)
        print(f"Extracted option type: {option_type}")
    else:
        print("No option type found")
    
    # Extract expiration date
    expiration_pattern = r'(?:expiring|expires?)\s+((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t)?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)|(?:expiring|expires?)\s+(?:on|at|by)?\s+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})|(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})|(?:(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t)?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)|(?:expiring|expires?)\s+(?:on|at|by)?\s+((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t)?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)'
    
    expiration_match = re.search(expiration_pattern, query, re.IGNORECASE)
    if expiration_match:
        print(f"Expiration match found: {expiration_match.group()}")
        groups = expiration_match.groups()
        print(f"Match groups: {[g for g in groups if g is not None]}")
        
        # Find the first non-None group which could be our date
        date_str = next((g for g in groups if g is not None), None)
        if date_str:
            print(f"Date string: {date_str}")
            
            # Remove ordinal suffixes
            date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
            print(f"Cleaned date: {date_str}")
            
            try:
                parsed_date = parser.parse(date_str)
                formatted = parsed_date.strftime('%Y-%m-%d')
                print(f"Parsed date: {formatted}")
            except Exception as e:
                print(f"Error parsing date: {e}")
    else:
        print("No expiration match found")
        
        # Try alternate pattern just for month and day with year
        alt_pattern = r'(?:expiring|expires?).*?((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t)?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:\s+\d{4})?)'
        alt_match = re.search(alt_pattern, query, re.IGNORECASE)
        if alt_match:
            print(f"Alternative match found: {alt_match.group(1)}")
            date_str = alt_match.group(1)
            date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
            print(f"Cleaned alt date: {date_str}")
            
            try:
                parsed_date = parser.parse(date_str)
                formatted = parsed_date.strftime('%Y-%m-%d')
                print(f"Parsed alt date: {formatted}")
            except Exception as e:
                print(f"Error parsing alt date: {e}")

if __name__ == "__main__":
    test_stop_loss_query()