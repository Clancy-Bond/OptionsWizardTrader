#!/usr/bin/env python3
"""
Test the strike price formatting fix specifically for TSLA
"""
from polygon_integration import get_simplified_unusual_activity_summary

def test_tsla_format():
    """Test the TSLA unusual activity formatting"""
    ticker = "TSLA"
    print(f"\nTesting unusual activity formatting for {ticker}...\n")
    
    # Get the unusual activity summary
    summary = get_simplified_unusual_activity_summary(ticker)
    
    # Print the formatted output
    print("\n===== UNUSUAL OPTIONS ACTIVITY OUTPUT =====\n")
    print(summary)
    
    # Check if the issue is fixed
    if f"(${ticker}.00)" in summary:
        print(f"\n❌ The issue is still present! Found '(${ticker}.00)' in the output.")
    else:
        print("\n✅ The issue appears to be fixed! Proper strike price formatting is being used.")
    
    # Look for the corrected format
    import re
    strike_formats = re.findall(r"in-the-money \(\$\d+\.\d+\)", summary)
    if strike_formats:
        print(f"\nFound the following properly formatted strike prices: {strike_formats}")
    else:
        print("\nCouldn't find any 'in-the-money ($X.XX)' formats in the output.")

if __name__ == "__main__":
    test_tsla_format()