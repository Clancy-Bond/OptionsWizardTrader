"""
Test script to view the TSLA unusual options activity format
"""
import polygon_integration

def test_tsla_unusual_activity():
    """Test the unusual options activity for TSLA"""
    ticker = "TSLA"
    print(f"Getting unusual options activity for {ticker}...")
    
    # Get the formatted output
    result = polygon_integration.get_simplified_unusual_activity_summary(ticker)
    
    print("\nFormatted Output:")
    print("=" * 60)
    print(result)
    print("=" * 60)

if __name__ == "__main__":
    test_tsla_unusual_activity()