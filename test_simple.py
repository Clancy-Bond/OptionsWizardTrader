#!/usr/bin/env python3
"""
Simple test script to check the unusual activity format
"""
from polygon_integration import get_simplified_unusual_activity_summary

def test_simple_format():
    """Test the format of unusual options activity in a simple way"""
    ticker = "AAPL"
    print(f"Getting unusual options activity for {ticker}...")
    
    # Get the summary
    summary = get_simplified_unusual_activity_summary(ticker)
    
    # Print just enough to see the format
    print("\nFirst 300 characters of the output:")
    print(summary[:300])
    
    # Just verify a few key formatting points
    format_checks = [
        ("strongly", "strongly" in summary),
        ("Inc.", f"{ticker}, Inc." in summary),
        ("in-the-money", "in-the-money" in summary),
        ("purchased", ", purchased" in summary),
        ("bold premium", "**$" in summary)
    ]
    
    print("\nFormat checks:")
    for name, passed in format_checks:
        print(f"  {'✓' if passed else '✗'} {name}")

if __name__ == "__main__":
    test_simple_format()