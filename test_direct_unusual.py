"""
Direct test for the new unusual options activity formatting
"""
import sys
from polygon_integration import get_simplified_unusual_activity_summary

def test_direct(ticker):
    """
    Test the direct API call to unusual options activity with updated formatting
    """
    print(f"\n===== TESTING UNUSUAL OPTIONS ACTIVITY FOR {ticker} =====\n")
    
    # Get the unusual activity directly from the function
    activity_summary = get_simplified_unusual_activity_summary(ticker)
    
    # Display the results
    print("\n===== FORMATTED OUTPUT =====\n")
    print(activity_summary)
    
    # Check for specific formatting elements
    if "Unusual activity score:" not in activity_summary:
        print("\n✅ Unusualness score has been removed")
    else:
        print("\n❌ Unusualness score is still present")
        
    # Check timestamp format - should only show the date (MM/DD/YY) now
    if "occurred at" in activity_summary:
        time_index = activity_summary.find("occurred at") + len("occurred at")
        timestamp_part = activity_summary[time_index:time_index+50].strip()
        print(f"\nTimestamp format: {timestamp_part.split()[0]}")
        
        # Check if time (HH:MM:SS) is present
        if ":" in timestamp_part:
            print("❌ Time portion is still present in the timestamp")
        else:
            print("✅ Timestamp format only shows the date as requested")
    else:
        print("\n❓ Could not find timestamp in output")
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    else:
        ticker = "TSLA"  # Default test with TSLA
        
    test_direct(ticker)