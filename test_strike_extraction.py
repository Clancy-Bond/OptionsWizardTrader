"""
Test the strike price extraction function directly
"""

def extract_strike_from_symbol(symbol):
    """Extract actual strike price from option symbol like O:TSLA250417C00252500"""
    if not symbol or not symbol.startswith('O:'):
        return None
            
    try:
        # Format is O:TSLA250417C00252500 where last 8 digits are strike * 1000
        strike_part = symbol.split('C')[-1] if 'C' in symbol else symbol.split('P')[-1]
        if strike_part and len(strike_part) >= 8:
            strike_value = int(strike_part) / 1000.0
            return f"{strike_value:.2f}"
        return None
    except (ValueError, IndexError):
        return None

# Test the function with some examples
def test_strike_extraction():
    print("Testing strike price extraction...")
    
    test_cases = [
        ("O:TSLA250417C00252500", "252.50"),
        ("O:TSLA250417P00260000", "260.00"),
        ("O:SPY250417C00500000", "500.00"),
        ("O:AAPL250417P00150000", "150.00"),
        ("O:MSFT250417C00400000", "400.00"),
        ("O:GOOG250417P00150000", "150.00"),
        ("INVALID", None),
    ]
    
    for symbol, expected in test_cases:
        result = extract_strike_from_symbol(symbol)
        if result == expected:
            print(f"✅ {symbol} → {result}")
        else:
            print(f"❌ {symbol} → got {result}, expected {expected}")

if __name__ == "__main__":
    test_strike_extraction()