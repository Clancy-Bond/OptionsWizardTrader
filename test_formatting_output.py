#!/usr/bin/env python3
"""
Test script to show the unusual options activity output with updated formatting
"""
import re
from polygon_integration import get_simplified_unusual_activity_summary

def test_unusual_activity(ticker="AAPL"):
    """
    Test the unusual activity detection with new formatting
    """
    print(f"\n===== Testing Unusual Options Activity for {ticker} =====\n")
    
    activity_summary = get_simplified_unusual_activity_summary(ticker)
    print("\n===== FORMATTED OUTPUT =====\n")
    print(activity_summary)
    
    # Format tests
    checks = [
        ("✅" if "strongly bullish activity for" in activity_summary or 
                "strongly bearish activity for" in activity_summary else "❌", 
         "Using 'strongly bullish/bearish activity for [Ticker], Inc.' format"),
        
        ("✅" if "**million bullish**" in activity_summary or 
                "**million bearish**" in activity_summary else "❌", 
         "Bolding 'million bullish/bearish' text"),
        
        ("✅" if re.search(r"in-the-money \(\$\d+\.\d+\)", activity_summary) else "❌", 
         "Using 'in-the-money ($245.00)' format"),
        
        ("✅" if "occurred on" in activity_summary and 
                not re.search(r"occurred (on|at) \d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}", activity_summary) else "❌", 
         "Date format without time component"),
        
        ("✅" if "Unusual activity score:" not in activity_summary else "❌", 
         "Removed 'Unusual activity score' line")
    ]
    
    print("\n===== FORMAT VERIFICATION =====\n")
    for check_result, check_description in checks:
        print(f"{check_result} {check_description}")

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    test_unusual_activity(ticker)