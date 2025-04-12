"""
Test unusual options activity for a specific ticker to check the enhanced summary format
"""
from polygon_integration import get_simplified_unusual_activity_summary

def test_unusual_summary(ticker):
    """
    Test the enhanced unusual activity summary format
    """
    print(f"\nGetting unusual activity summary for {ticker}...")
    summary = get_simplified_unusual_activity_summary(ticker)
    print(summary)

if __name__ == "__main__":
    test_unusual_summary("TSLA")