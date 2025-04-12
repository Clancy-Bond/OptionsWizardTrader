"""
Debug script to troubleshoot unusual options activity detection
"""
import json
import re
from polygon_integration import get_unusual_options_activity, get_simplified_unusual_activity_summary

def debug_unusual_activity(ticker):
    """
    Detailed debugging of unusual options activity detection
    """
    print(f"\n===== Debugging Unusual Activity Detection for {ticker} =====\n")
    
    # Get only top 3 unusual activities for faster processing
    activity = get_unusual_options_activity(ticker)
    if not activity:
        print(f"No unusual activity found for {ticker}")
        return
        
    # Limit to top 3 activities for faster testing
    activity = activity[:3]
    
    # Print detailed info about each activity
    for i, option in enumerate(activity):
        print(f"\nOPTION {i+1}: {option['contract']}")
        print(f"  Sentiment: {option['sentiment']}")
        print(f"  Unusualness Score: {option.get('unusualness_score', 'N/A')}")
        if 'timestamp_human' in option:
            print(f"  Timestamp: {option['timestamp_human']}")
        print(f"  Volume: {option['volume']}")
        print(f"  Premium: ${option['premium']:,.2f}")
    
    # Get the simplified summary with timestamps
    print("\n===== SIMPLIFIED SUMMARY =====")
    summary = get_simplified_unusual_activity_summary(ticker)
    print(summary)
    
    # Verify timestamp format in the summary
    if "AM ET" in summary or "PM ET" in summary:
        print("\n✅ Summary includes timestamps in AM/PM format with ET timezone")
    else:
        print("\n❌ AM/PM timestamp format not found in summary")
        
    # Verify sentiment matching
    bullish_match = "Largest bullish trade occurred at:" in summary and "bullish activity" in summary
    bearish_match = "Largest bearish trade occurred at:" in summary and "bearish activity" in summary
    
    if bullish_match:
        print("✅ Bullish timestamp correctly associated with bullish activity")
    elif bearish_match:
        print("✅ Bearish timestamp correctly associated with bearish activity")
    else:
        print("❓ Couldn't verify sentiment-timestamp association")

if __name__ == "__main__":
    # Test with AAPL which typically has less options than SPY for faster processing
    debug_unusual_activity("AAL")