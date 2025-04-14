"""
Test script to verify the date format in unusual options activity
"""

import polygon_integration

def test_date_format():
    """
    Test the date format in unusual options activity output
    """
    print("Testing date format in unusual options activity output...")
    
    # Get unusual options activity for a specific ticker
    ticker = "TSLA"
    print(f"Getting unusual options activity for {ticker}...")
    
    # Get the output as a Discord message would
    result = polygon_integration.get_unusual_options_activity_report(ticker)
    
    # Print the result
    print("\nOutput:")
    print(result)
    
    print("\nTest complete!")

if __name__ == "__main__":
    test_date_format()