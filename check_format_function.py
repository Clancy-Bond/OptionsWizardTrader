"""
Test the formatting function directly without making API calls
"""

import re
import datetime
from polygon_integration import format_largest_flow

def test_format():
    """Test the formatting of unusual activity output"""
    # Mock flow data
    mock_flow = {
        'ticker': 'TSLA',
        'sentiment': 'bullish',
        'option_symbol': 'O:TSLA250417C00252500',
        'premium_millions': 4.7,
        'expiry': '2025-04-17',
        'strike': 252.5,
        'is_in_the_money': True,
        'trade_time': datetime.datetime(2025, 4, 14, 10, 30, 0)
    }
    
    # Format the flow
    formatted = format_largest_flow(mock_flow)
    print("FORMATTED OUTPUT:")
    print("-" * 60)
    print(formatted)
    print("-" * 60)
    
    # Check formatting requirements
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
    # Check if format_largest_flow exists
    try:
        from polygon_integration import format_largest_flow
        test_format()
    except ImportError:
        print("Error: format_largest_flow function not found in polygon_integration")
        print("Looking for similar functions...")
        with open("polygon_integration.py") as f:
            content = f.read()
            format_functions = re.findall(r"def\s+(format_[a-zA-Z_]+)", content)
            if format_functions:
                print(f"Found format functions: {format_functions}")
            else:
                print("No format functions found")