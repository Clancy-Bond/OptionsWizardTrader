"""
Test script for unusual options activity functionality
"""

from unusual_activity import get_unusual_options_activity, get_simplified_unusual_activity_summary
from polygon_integration import get_current_price

def test_unusual_options_activity():
    # Test getting the current price (previously failed with NOT_AUTHORIZED)
    ticker = "SPY"
    price = get_current_price(ticker)
    print(f"{ticker} current price: {price}")
    
    # Test unusual options activity
    unusual_activity = get_unusual_options_activity(ticker)
    print(f"Unusual options activity found: {len(unusual_activity)} items")
    
    # Test simplified summary
    summary = get_simplified_unusual_activity_summary(ticker)
    print(f"Summary: {summary}")
    
    return price is not None

if __name__ == "__main__":
    success = test_unusual_options_activity()
    print(f"Test {'PASSED' if success else 'FAILED'}")