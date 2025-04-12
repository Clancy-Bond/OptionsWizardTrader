#!/usr/bin/env python3
"""
Test script to check if the unusual options activity formatting has been correctly updated
"""
from polygon_integration import get_simplified_unusual_activity_summary

def test_formatting():
    """Test the updated formatting for unusual options activity"""
    ticker = "TSLA"
    print(f"\nTesting unusual activity formatting for {ticker}...\n")
    
    # Get the unusual activity summary
    summary = get_simplified_unusual_activity_summary(ticker)
    
    # Print the formatted output
    print("\n===== UNUSUAL OPTIONS ACTIVITY OUTPUT =====\n")
    print(summary)
    
    # Check if the updated format is present
    if "strongly bullish activity for TSLA, Inc." in summary or "strongly bearish activity for TSLA, Inc." in summary:
        print("\n✅ Found 'strongly bullish/bearish activity for TSLA, Inc.' format")
    else:
        print("\n❌ Did not find 'strongly bullish/bearish activity for TSLA, Inc.' format")
    
    if "in-the-money ($" in summary:
        print("✅ Found 'in-the-money ($X.XX)' format")
    else:
        print("❌ Did not find 'in-the-money ($X.XX)' format")
        
    if ", purchased " in summary:
        print("✅ Found purchase date at the end of option description")
    else:
        print("❌ Did not find purchase date at the end of option description")
        
    if "**$" in summary and " million bullish**" in summary or " million bearish**" in summary:
        print("✅ Found bolded premium amounts")
    else:
        print("❌ Did not find bolded premium amounts")
    
    # Check for the old format that should be gone
    if "-the-money ($" in summary:
        print("❌ Still found old format '-the-money ($X)' in output")
    else:
        print("✅ Successfully removed old format '-the-money ($X)'")

if __name__ == "__main__":
    test_formatting()