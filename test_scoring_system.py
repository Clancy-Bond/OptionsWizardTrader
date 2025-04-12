"""
Test the scoring system and format of the unusual options activity
"""
from polygon_integration import calculate_unusualness_score, get_simplified_unusual_activity_summary
import re

def test_unusual_summary_format(ticker):
    """Test the format of the unusual options activity summary"""
    print(f"\n===== Testing Unusual Activity Summary Format for {ticker} =====\n")
    
    # Get summary
    summary = get_simplified_unusual_activity_summary(ticker)
    print(summary)
    
    # Extract timestamp and verify format
    timestamp_pattern = r"Largest \w+ trade occurred at: (.*?)\n"
    match = re.search(timestamp_pattern, summary)
    
    if match:
        timestamp = match.group(1)
        print(f"\nExtracted timestamp: {timestamp}")
        
        # Check format
        if 'AM ET' in timestamp or 'PM ET' in timestamp:
            print("✅ Timestamp uses AM/PM format with ET timezone")
        else:
            print("❌ Timestamp does not use AM/PM format with ET timezone")
            
        # Check if sentiment is consistent
        if "Largest bullish trade" in summary and "bullish activity" in summary:
            print("✅ Bullish timestamp correctly associated with bullish activity")
        elif "Largest bearish trade" in summary and "bearish activity" in summary:
            print("✅ Bearish timestamp correctly associated with bearish activity")
        else:
            print("❓ Couldn't verify sentiment-timestamp association")
    else:
        print("❌ No timestamp found in the summary")

if __name__ == "__main__":
    # Test with SPY for faster processing
    test_unusual_summary_format("SPY")