"""
Direct test for the new unusual options activity scoring system
Bypasses Discord bot to test directly
"""
from polygon_integration import get_unusual_options_activity
from polygon_integration import get_simplified_unusual_activity_summary

def test_unusual_activity(ticker):
    """
    Test the unusual options activity detection directly
    """
    print(f"\n===== Testing Unusual Options Activity for {ticker} =====\n")
    
    # Get the raw unusual activity data
    activity = get_unusual_options_activity(ticker)
    
    # Print the detailed data including scores
    if activity:
        print(f"Found {len(activity)} unusual options activities:\n")
        for i, item in enumerate(activity):
            print(f"OPTION {i+1}: {item['contract']}")
            print(f"  Sentiment: {item['sentiment']}")
            print(f"  Volume: {item['volume']}")
            print(f"  Premium: ${item['premium']:,.2f}")
            print(f"  Unusualness Score: {item.get('unusualness_score', 'N/A')}")
            
            # Print score breakdown if available
            if 'score_breakdown' in item:
                breakdown = item['score_breakdown']
                print("  Score Breakdown:")
                for k, v in breakdown.items():
                    if k not in ['total_volume', 'total_premium', 'largest_trade']:
                        print(f"    {k}: {v}")
            print()
    else:
        print("No unusual options activity found.")
    
    # Get and print the simplified summary
    print("\n===== Simplified Summary =====\n")
    summary = get_simplified_unusual_activity_summary(ticker)
    print(summary)

if __name__ == "__main__":
    ticker = "TSLA"
    test_unusual_activity(ticker)