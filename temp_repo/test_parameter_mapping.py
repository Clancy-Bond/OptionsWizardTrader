"""
Simple test script to manually verify our parameter mapping logic works correctly.
This script does not import the actual bot but implements similar logic to the parse_query method.
"""

def parse_query_test(info):
    """
    Test function that simulates the parse_query method's parameter mapping logic
    """
    # Ensure parameter naming consistency - handle 'strike' vs 'strike_price'
    if 'strike' in info and info['strike'] is not None:
        info['strike_price'] = info['strike']
    
    # Ensure parameter naming consistency - handle 'expiration' vs 'expiration_date'
    if 'expiration' in info and info['expiration'] is not None:
        info['expiration_date'] = info['expiration']
    
    return info

def run_tests():
    """Run the parameter mapping tests"""
    # Test 1: Only strike field
    info1 = {'ticker': 'AAPL', 'strike': 200, 'option_type': 'call'}
    before1 = info1.copy()  # Make a copy to preserve original state
    result1 = parse_query_test(info1)
    print("\n=== Test 1: Only strike field ===")
    print(f"Before: {before1}")
    print(f"After: {result1}")
    print(f"Has 'strike': {'strike' in result1}")
    print(f"Has 'strike_price': {'strike_price' in result1}")
    
    # Test 2: Only expiration field
    info2 = {'ticker': 'TSLA', 'strike_price': 250, 'option_type': 'put', 'expiration': '2025-04-18'}
    before2 = info2.copy()  # Make a copy to preserve original state
    result2 = parse_query_test(info2)
    print("\n=== Test 2: Only expiration field ===")
    print(f"Before: {before2}")
    print(f"After: {result2}")
    print(f"Has 'expiration': {'expiration' in result2}")
    print(f"Has 'expiration_date': {'expiration_date' in result2}")
    
    # Test 3: Both fields present already
    info3 = {
        'ticker': 'META', 
        'strike': 450, 
        'strike_price': 450,
        'option_type': 'call', 
        'expiration': '2025-06-20',
        'expiration_date': '2025-06-20'
    }
    before3 = info3.copy()  # Make a copy to preserve original state
    result3 = parse_query_test(info3)
    print("\n=== Test 3: Both fields already present ===")
    print(f"Before: {before3}")
    print(f"After: {result3}")
    
    # Test 4: Missing fields
    info4 = {'ticker': 'NVDA', 'option_type': 'call'}
    before4 = info4.copy()  # Make a copy to preserve original state
    result4 = parse_query_test(info4)
    print("\n=== Test 4: Missing fields ===")
    print(f"Before: {before4}")
    print(f"After: {result4}")
    print(f"Has 'strike': {'strike' in result4}")
    print(f"Has 'strike_price': {'strike_price' in result4}")
    print(f"Has 'expiration': {'expiration' in result4}")
    print(f"Has 'expiration_date': {'expiration_date' in result4}")

if __name__ == "__main__":
    run_tests()