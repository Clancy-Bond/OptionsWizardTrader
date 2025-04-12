#!/usr/bin/env python3
"""
Direct test for the new unusual options activity scoring system
Bypasses Discord bot to test directly 
"""
import re
from polygon_integration import get_simplified_unusual_activity_summary

def test_unusual_activity(ticker):
    """
    Test the unusual options activity detection directly
    Focus on just the first few options to complete quickly
    """
    print(f"\n===== Testing Unusual Options Activity Format for {ticker} =====\n")
    
    # Directly access the polygon_integration.py module to set max_options_to_process to 10
    import polygon_integration
    original_max = polygon_integration.max_options_to_process if hasattr(polygon_integration, 'max_options_to_process') else 50
    
    # Set max options to 10 to make the test run faster
    polygon_integration.max_options_to_process = 10
    
    # Get the summary directly from the function
    summary = get_simplified_unusual_activity_summary(ticker)
    
    # Restore original value
    polygon_integration.max_options_to_process = original_max
    
    # Print the first 500 characters to see the formatting
    print(summary[:500] + "...\n")
    
    # Extract and print just the first few lines to focus on formatting
    first_bullet = re.search(r'•.*?\n\n', summary, re.DOTALL)
    if first_bullet:
        print("First bullet point (format check):")
        print(first_bullet.group(0))
    
    # Check for each format element
    checks = {
        "strongly bullish/bearish": "strongly" in summary,
        "Inc. suffix": f"{ticker}, Inc." in summary,
        "bolded premium": "**$" in summary and "million" in summary and "**" in summary,
        "in-the-money format": "in-the-money ($" in summary,
        "purchase date": ", purchased " in summary
    }
    
    print("\n=== Format Verification ===")
    for item, passed in checks.items():
        print(f"{'✅' if passed else '❌'} {item}")
    
    # Overall assessment
    if all(checks.values()):
        print("\n✅ All formatting requirements have been successfully implemented!")
    else:
        print("\n❌ Some formatting requirements are still missing. Check the report above.")

if __name__ == "__main__":
    # Test with a ticker that typically has unusual options activity
    test_unusual_activity("AAPL")  # Using AAPL for a quicker test