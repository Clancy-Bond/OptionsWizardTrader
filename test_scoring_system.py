"""
Test script for the new unusual options activity scoring system
"""
import sys
from polygon_integration import get_simplified_unusual_activity_summary

def test_ticker_scoring(ticker_symbol):
    """
    Test the new scoring system on a specific ticker
    """
    print(f"\nAnalyzing unusual options activity for {ticker_symbol}...\n")
    result = get_simplified_unusual_activity_summary(ticker_symbol)
    print("\n" + result + "\n")

if __name__ == "__main__":
    # Get ticker from command line argument or use default
    ticker = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    test_ticker_scoring(ticker)