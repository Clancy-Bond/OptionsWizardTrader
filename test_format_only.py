"""
Test only the formatting of the unusual activity response
This is a minimal test that doesn't require API calls
"""

import re
import polygon_integration

def main():
    """Test strike price extraction and output formatting"""
    # Test the extraction function
    test_symbols = [
        ("O:TSLA250417C00252500", "252.50"),
        ("O:AAPL240419P00170000", "170.00"),
        ("O:SPY250117C00535000", "535.00"),
        ("O:NVDA250620C01200000", "1200.00")
    ]
    
    print("Testing strike price extraction:")
    for symbol, expected in test_symbols:
        strike = polygon_integration.extract_strike_from_symbol(symbol)
        result = "✅" if strike == expected else "❌"
        print(f"{result} {symbol} → {strike} (expected {expected})")
    
    # The real function we're testing is get_largest_flow_for_ticker
    # But we don't want to make API calls, so we'll just verify the format_output part
    
    # Create a test output using the formatting pattern
    import datetime
    
    mock_flow = {
        'ticker': 'TSLA',
        'sentiment': 'bullish',
        'option_symbol': 'O:TSLA250417C00252500',
        'premium_millions': 4.7,
        'expiry': '2025-04-17',
        'is_in_the_money': True,
        'trade_time': datetime.datetime(2025, 4, 14, 10, 30, 0)
    }
    
    # Call the formatting part directly
    print("\nFormatting test:")
    formatted = polygon_integration.format_largest_flow(mock_flow)
    print(formatted)
    
    # Verify formatting requirements
    checks = {
        "Strike price format": (
            r'in-the-money \((\d+\.\d+)\)',
            lambda m: f"✅ Found numeric strike price: {m.group(0)}" if m else "❌ Missing numeric strike price"
        ),
        "Expiration date format": (
            r'expiring (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found MM/DD/YY expiration: {m.group(0)}" if m else "❌ Missing MM/DD/YY expiration"
        ),
        "Purchase date": (
            r'purchased (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found purchase date: {m.group(0)}" if m else "❌ Missing purchase date"
        ),
        "No bet wording": (
            r'bullish bet|bearish bet',
            lambda m: "❌ Contains unwanted 'bet' wording" if m else "✅ No 'bet' wording"
        ),
        "No 'occurred at'": (
            r'occurred at',
            lambda m: "❌ Contains unwanted 'occurred at' text" if m else "✅ No 'occurred at' text"
        ),
        "No 'on' before date": (
            r'expiring on',
            lambda m: "❌ Contains unwanted 'expiring on' text" if m else "✅ No 'expiring on' text"
        ),
        "No ticker in strike": (
            r'in-the-money \(\$[A-Z]+',
            lambda m: "❌ Contains ticker symbol in strike price" if m else "✅ No ticker in strike price"
        ),
        "No X-the-money format": (
            r'\d+-the-money',
            lambda m: "❌ Contains X-the-money format" if m else "✅ No X-the-money format"
        ),
        "Has bolded millions": (
            r'\*\*\$\d+\.\d+ million (bullish|bearish)\*\*',
            lambda m: f"✅ Properly bolded millions: {m.group(0)}" if m else "❌ Missing bolded millions"
        )
    }
    
    # Run all checks
    all_passed = True
    for check_name, (pattern, result_fn) in checks.items():
        match = re.search(pattern, formatted)
        
        # For 'No X' checks, we want match to be None
        expected_match = "No" not in check_name
        
        if (match and expected_match) or (not match and not expected_match):
            print(f"{check_name}: {result_fn(match)}")
        else:
            all_passed = False
            if "No" in check_name and match:
                # For 'No X' checks, finding a match is a failure
                print(f"{check_name}: ❌ Found forbidden pattern: {match.group(0)}")
            else:
                print(f"{check_name}: {result_fn(match)}")
    
    # Overall result
    if all_passed:
        print("\n✅ ALL FORMAT REQUIREMENTS PASSED!")
    else:
        print("\n❌ SOME FORMAT REQUIREMENTS FAILED!")

if __name__ == "__main__":
    main()