"""
Test script to directly verify the updated unusual activity output format
"""
import sys
from polygon_integration import get_simplified_unusual_activity_summary

def test_unusual_activity_format(ticker):
    """Test the new updated format for unusual activity"""
    summary = get_simplified_unusual_activity_summary(ticker)
    print("\n===== UNUSUAL ACTIVITY FORMAT TEST =====\n")
    print(summary)
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    else:
        ticker = "AAPL"
    
    test_unusual_activity_format(ticker)