"""
Test script to verify the fixes to the regex patterns in discord_bot.py
"""

from discord_bot import OptionsBotNLP

def test_with_dollar_strike():
    """Test with a dollar sign in the strike price"""
    
    # Query with $ in strike price
    query = "Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    print(f"Query: {query}")
    
    # Initialize the NLP processor
    nlp = OptionsBotNLP()
    
    # Parse the query
    result = nlp.parse_query(query)
    
    # Print the result
    request_type, info = result
    print(f"Request type: {request_type}")
    print(f"Info: {info}")
    
    # Verify the strike price
    if info['strike'] == 270.0:
        print("SUCCESS: Strike price correctly extracted as 270.0")
    else:
        print(f"ERROR: Strike price extracted as {info['strike']}, expected 270.0")
    
    # Verify the expiration date
    if info['expiration'] == '2025-04-04':
        print("SUCCESS: Expiration date correctly parsed as 2025-04-04")
    else:
        print(f"ERROR: Expiration date parsed as {info['expiration']}, expected 2025-04-04")

def main():
    """Main test function"""
    print("Testing pattern fixes in discord_bot.py...\n")
    test_with_dollar_strike()

if __name__ == "__main__":
    main()