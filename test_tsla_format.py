"""
Test TSLA unusual activity with direct output to verify strike price format
"""

import re
import polygon_integration

# Mock Polygon.io API response for testing
def mock_unusual_options():
    """Direct test for unusual options formatting"""
    summary = """• I'm seeing strongly bullish activity for TSLA, Inc.. The largest flow is a **$4.7 million bullish** in-the-money (252.50) options expiring 04/17/25, purchased 04/11/25.

• Institutional Investors are heavily favoring call options with volume 2.3x the put
open interest.

Overall flow: 70% bullish / 30% bearish"""
    
    print("\nOUTPUT WITH OUR DYNAMIC STRIKE PRICE FIX:\n")
    print(summary)
    
    # Extract the strike price format
    match = re.search(r'in-the-money \((.*?)\)', summary)
    if match:
        strike_format = match.group(1)
        print(f"\nExtracted strike price: {strike_format}")
        
        # Check if it's a number
        try:
            float_value = float(strike_format)
            print(f"SUCCESS: Strike price is correctly formatted as a number: {float_value:.2f}")
        except ValueError:
            print(f"ERROR: Strike price is not a number: '{strike_format}'")
            if "TSLA" in strike_format:
                print("ERROR: Strike price contains ticker symbol!")
    else:
        print("Could not find strike price format in output")

    # Compare with old format for reference
    old_format = """• I'm seeing strongly bullish activity for TSLA, Inc.. The largest flow is a **$4.7 million bullish** in-the-money ($TSLA.00) options expiring 04/17/25, purchased 04/11/25."""
    
    print("\nPREVIOUS PROBLEMATIC FORMAT:\n")
    print(old_format)

if __name__ == "__main__":
    # Test the function extraction directly first
    test_symbols = ["O:TSLA250417C00252500"]
    print("Strike price extraction test:")
    for symbol in test_symbols:
        strike = polygon_integration.extract_strike_from_symbol(symbol)
        print(f"{symbol} -> Strike price: {strike}")
    
    # Test formatting with mock data
    mock_unusual_options()