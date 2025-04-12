#!/usr/bin/env python3
"""
Simple script to test unusual options activity formatting directly
"""
import re
import sys
from polygon_integration import get_simplified_unusual_activity_summary

def test_unusual_activity(ticker="AAPL"):
    """
    Get simplified unusual activity summary and verify its formatting
    """
    print(f"\n===== Testing Unusual Activity Format for {ticker} =====\n")
    
    try:
        # Get the unusual activity summary
        activity_summary = get_simplified_unusual_activity_summary(ticker)
        
        # Print the formatted output
        print("\n===== UNUSUAL ACTIVITY OUTPUT =====\n")
        print(activity_summary)
        
        # Verify formatting requirements
        format_checks = [
            ("✅" if "strongly bullish activity for" in activity_summary.lower() or 
                    "strongly bearish activity for" in activity_summary.lower() else "❌",
             "Uses 'strongly bullish/bearish activity for [Ticker], Inc.' format"),
            
            ("✅" if "**million bullish**" in activity_summary or 
                    "**million bearish**" in activity_summary else "❌",
             "Bolds 'million bullish/bearish' text"),
            
            ("✅" if re.search(r"in-the-money \(\$\d+\.\d+\)", activity_summary) else "❌",
             "Uses 'in-the-money ($245.00)' format"),
            
            ("✅" if re.search(r"occurred on \d{2}/\d{2}/\d{2}", activity_summary) and
                    not re.search(r"occurred (on|at) \d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}", activity_summary) else "❌",
             "Shows date without time component"),
            
            ("✅" if "Unusual activity score:" not in activity_summary else "❌",
             "Does not show unusualness score")
        ]
        
        print("\n===== FORMAT VERIFICATION =====\n")
        for check_result, check_description in format_checks:
            print(f"{check_result} {check_description}")
    
    except Exception as e:
        print(f"Error testing unusual activity format: {e}")

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    test_unusual_activity(ticker)