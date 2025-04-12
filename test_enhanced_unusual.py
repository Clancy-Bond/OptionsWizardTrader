"""
Test the enhanced unusual options activity detection with real-time transaction data
"""
import json
from polygon_integration import get_unusual_options_activity, get_simplified_unusual_activity_summary

def test_unusual_activity_with_timestamps(ticker):
    """
    Test the enhanced unusual activity detection with timestamps
    """
    print(f"\n===== Testing Enhanced Unusual Options Activity for {ticker} =====\n")
    
    # Get raw unusual activity data
    activity = get_unusual_options_activity(ticker)
    
    if not activity:
        print(f"No unusual activity found for {ticker}")
        return
    
    print(f"Found {len(activity)} unusual activities for {ticker}:")
    
    # Print details including timestamps
    for i, item in enumerate(activity):
        print(f"\nOPTION {i+1}: {item['contract']}")
        print(f"  Sentiment: {item['sentiment']}")
        print(f"  Unusualness Score: {item.get('unusualness_score', 'N/A')}")
        print(f"  Volume: {item['volume']} contracts")
        print(f"  Premium: ${item['premium']:,.2f}")
        
        # Print timestamp information if available
        if 'timestamp_human' in item:
            print(f"  Trade Time: {item['timestamp_human']}")
        elif 'transaction_date' in item:
            print(f"  Trade Date: {item['transaction_date']}")
            
        # Print exchange information if available
        if 'exchange' in item:
            print(f"  Exchange: {item['exchange']}")
            
        # Print score breakdown details
        if 'score_breakdown' in item:
            print("  Score Breakdown:")
            for k, v in item['score_breakdown'].items():
                if k not in ['total_volume', 'total_premium', 'largest_trade']:
                    print(f"    {k}: {v}")
    
    # Show the simplified summary
    print("\n===== Simplified Summary =====\n")
    summary = get_simplified_unusual_activity_summary(ticker)
    print(summary)

if __name__ == "__main__":
    test_unusual_activity_with_timestamps("TSLA")