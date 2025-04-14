"""
Test the strike price extraction and formatting
"""

from polygon_integration import extract_strike_from_symbol

def test_extraction():
    """Test strike price extraction from various option symbols"""
    test_cases = [
        ("O:TSLA250417C00252500", "252.50"),
        ("O:AAPL240419P00170000", "170.00"),
        ("O:SPY250117C00535000", "535.00"),
        ("O:NVDA250620C01200000", "1200.00"),
        ("O:TSLA250425P00245000", "245.00"),
        ("O:AMD250919C00150000", "150.00")
    ]
    
    print("TESTING STRIKE PRICE EXTRACTION:")
    print("-" * 50)
    
    all_passed = True
    for symbol, expected in test_cases:
        result = extract_strike_from_symbol(symbol)
        if result == expected:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            all_passed = False
        print(f"{status} {symbol} → {result} (expected {expected})")
    
    print("-" * 50)
    if all_passed:
        print("✅ ALL STRIKE PRICE EXTRACTIONS PASSED!")
    else:
        print("❌ SOME STRIKE PRICE EXTRACTIONS FAILED!")

if __name__ == "__main__":
    test_extraction()