"""
Direct test for the new unusual options activity scoring system
Bypasses Discord bot to test directly
"""
import json
import re
from polygon_integration import get_simplified_unusual_activity_summary

def test_unusual_activity(ticker):
    """
    Test the unusual options activity detection directly
    """
    print(f"\n===== Testing Unusual Options Activity for {ticker} =====\n")
    
    # Get the summary directly from the function
    summary = get_simplified_unusual_activity_summary(ticker)
    print(summary)
    
    # Verify AM/PM timestamp format with ET timezone
    if "AM ET" in summary or "PM ET" in summary:
        print("\n✅ AM/PM timestamp with ET timezone confirmed")
    else:
        print("\n❌ AM/PM timestamp format not found")
        
    # Check if timestamp is associated with the correct sentiment
    if "Largest bullish trade occurred at:" in summary and "bullish activity" in summary:
        print("✅ Bullish timestamp correctly associated with bullish activity")
    elif "Largest bearish trade occurred at:" in summary and "bearish activity" in summary:
        print("✅ Bearish timestamp correctly associated with bearish activity")
    else:
        print("❓ Couldn't verify sentiment-timestamp association")

if __name__ == "__main__":
    # Test with a ticker that typically has unusual options activity
    test_unusual_activity("AAPL")  # Using AAPL for faster processing