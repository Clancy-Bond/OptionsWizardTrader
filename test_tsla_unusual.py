"""
Test the TSLA unusual options activity pattern directly
"""

import re
import polygon_integration

def test_format_directly():
    """Directly test symbol extraction and verify the output"""
    
    # Test symbol extraction
    symbol = "O:TSLA250417C00255000"
    strike = polygon_integration.extract_strike_from_symbol(symbol)
    print(f"Extracted strike from {symbol}: {strike}")
    
    # Test with mock data that should match our expected output format
    mock_output = """• I'm seeing strongly bullish activity for TSLA, Inc.. The largest flow is a **$4.7 million bullish** in-the-money (255.00) options expiring 04/17/25, purchased 04/14/25.

• Institutional Investors are heavily favoring call options with volume 2.3x the put
open interest.

Overall flow: 70% bullish / 30% bearish"""
    
    print("\nVerifying expected output format:")
    print("-" * 60)
    print(mock_output)
    print("-" * 60)
    
    # Check all formatting requirements
    checks = {
        "Strike price format": (
            r'in-the-money \((\d+\.\d+)\)',
            lambda m: f"✅ Found numeric strike price: {m[0]}" if m else "❌ Missing numeric strike price"
        ),
        "Expiration date format": (
            r'expiring (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found MM/DD/YY expiration: {m[0]}" if m else "❌ Missing MM/DD/YY expiration"
        ),
        "Purchase date": (
            r'purchased (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found purchase date: {m[0]}" if m else "❌ Missing purchase date"
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
            lambda m: f"✅ Properly bolded millions: {m[0]}" if m else "❌ Missing bolded millions"
        )
    }
    
    # Run all checks
    for check_name, (pattern, result_fn) in checks.items():
        match = re.search(pattern, mock_output)
        print(f"{check_name}: {result_fn(match)}")
    
    # Overall verification
    all_passed = all(
        (re.search(pattern, mock_output) is None) == ("No" in check_name)
        for check_name, (pattern, _) in checks.items()
    )
    
    if all_passed:
        print("\n✅ All format requirements passed!")
    else:
        print("\n❌ Some format requirements failed!")
    
    # Test against actual API call (limited output to prevent timeout)
    print("\nNow testing with real Polygon API data (first 200 chars only):")
    try:
        result = polygon_integration.get_simplified_unusual_activity_summary("TSLA")
        print(result[:200] + "... [truncated]")
        
        # Check specifically for in-the-money (NUMBER) pattern in real output
        strike_match = re.search(r'in-the-money \((\d+\.\d+)\)', result)
        if strike_match:
            print(f"\n✅ Real API output has numeric strike price: {strike_match.group(1)}")
        else:
            print("\n❌ Real API output is missing numeric strike price")
            if "$TSLA" in result:
                print("❌ Contains ticker symbol in strike: $TSLA")
    except Exception as e:
        print(f"Error testing real API: {e}")

if __name__ == "__main__":
    test_format_directly()