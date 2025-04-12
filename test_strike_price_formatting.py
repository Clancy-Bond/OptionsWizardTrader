#!/usr/bin/env python3
"""
Test the fixed strike price formatting for in-the-money options
"""
import sys
from polygon_integration import get_simplified_unusual_activity_summary

def test_formatting(ticker="TSLA"):
    """
    Test the unusual options activity formatting for a given ticker
    """
    print(f"\n===== Testing strike price formatting for {ticker} =====\n")
    
    # Get the unusual options activity summary
    summary = get_simplified_unusual_activity_summary(ticker)
    
    # Print the formatted output
    print("\n===== UNUSUAL OPTIONS ACTIVITY OUTPUT =====\n")
    print(summary)
    
    # Check if the specific incorrect format is still present
    incorrect_format = f"(${ticker}.00)"
    if incorrect_format in summary:
        print(f"\n❌ Incorrect strike price formatting still present: {incorrect_format}")
    else:
        print("\n✅ The strike price formatting has been fixed")
        
        # Check if the proper format is now used
        import re
        matches = re.findall(r"in-the-money \(\$\d+\.\d+\)", summary)
        if matches:
            print(f"Found correctly formatted strikes: {matches}")
        else:
            print("No strike price formatting found in output")

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    test_formatting(ticker)