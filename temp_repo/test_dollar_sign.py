"""
Test script to check if the $ character is properly preserved in the query
"""

import re
from datetime import datetime
from dateutil import parser

def test_dollar_sign_pattern():
    """Test if $ character is preserved in patterns"""
    
    # Original query
    query = "Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    print(f"Original query: {query}")
    
    # Extract prices with standard pattern
    price_pattern = r'\$?(\d+\.?\d*)'
    price_matches = re.findall(price_pattern, query)
    print(f"Using \\$?(\d+\.?\d*): {price_matches}")
    
    # Check specifically for dollar sign pattern
    dollar_pattern = r'\$(\d+\.?\d*)'
    dollar_matches = re.findall(dollar_pattern, query)
    print(f"Using \\$(\d+\.?\d*): {dollar_matches}")
    
    # Make sure dollar sign is preserved
    preserved_query = f"Query with dollar sign: {query}"
    print(preserved_query)
    
    # Test the strike pattern
    strike_pattern = r'(?:\$(\d+\.?\d*))|(?:strike\s+(?:price\s+)?(?:of\s+)?\$?(\d+\.?\d*))|(?:strike\s+(?:price\s+)?(?:at\s+)?\$?(\d+\.?\d*))|(?:\$(\d+\.?\d*)\s+(?:calls?|puts?)\b)|(\d+\.?\d*)\s+(?:calls?|puts?)\b'
    strike_match = re.search(strike_pattern, query)
    if strike_match:
        print(f"Strike match found: {strike_match.group()}")
        groups = strike_match.groups()
        print(f"Strike match groups: {groups}")
        strike = next((g for g in groups if g is not None), None)
        if strike:
            print(f"Extracted strike price: {strike}")
        else:
            print("No strike price captured in groups")
    else:
        print("No strike pattern match found!")
    
def main():
    """Main test function"""
    print("Testing dollar sign handling in patterns...")
    test_dollar_sign_pattern()

if __name__ == "__main__":
    main()