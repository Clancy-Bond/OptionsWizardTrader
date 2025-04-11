"""
Test script to verify the exact query format that the user was having issues with.
"""

from discord_bot import OptionsBotNLP

def test_user_problematic_query():
    """Test the exact query format that user reported as problematic"""
    
    # Exact query that caused problems for the user
    query = '<@1354551896605589584> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"'
    print(f"Original query: {query}")
    
    # Remove bot mention
    processed_query = query.replace('<@1354551896605589584>', '').strip()
    print(f"Processed query: {processed_query}")
    
    # Initialize the NLP processor
    nlp = OptionsBotNLP()
    
    # Parse the query
    result = nlp.parse_query(processed_query)
    
    # Print the result
    request_type, info = result
    print(f"Request type: {request_type}")
    print(f"Extracted info:")
    for key, value in info.items():
        if value is not None:
            print(f"  {key}: {value}")
    
    # Verify key information
    if info['ticker'] == 'TSLA' and info['strike'] == 270.0 and info['expiration'] == '2025-04-04':
        print("\nTEST RESULT: SUCCESS - All information correctly extracted")
    else:
        print("\nTEST RESULT: FAILURE - Information not correctly extracted")
        print(f"Expected: ticker='TSLA', strike=270.0, expiration='2025-04-04'")
        print(f"Got: ticker='{info['ticker']}', strike={info['strike']}, expiration='{info['expiration']}'")

def main():
    """Main test function"""
    print("Testing user's problematic query format...\n")
    test_user_problematic_query()

if __name__ == "__main__":
    main()