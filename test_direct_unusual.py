"""
Direct test for the new unusual options activity scoring system
Bypasses Discord bot to test directly
"""

import polygon_integration

def test_unusual_activity(ticker):
    """
    Test the unusual options activity detection directly
    """
    print(f"Testing unusual options activity for {ticker}...\n")
    
    # Get the summary without Discord bot formatting
    summary = polygon_integration.get_simplified_unusual_activity_summary(ticker)
    
    # Print the summary
    print("UNUSUAL OPTIONS ACTIVITY\n")
    print(summary)
    
    # Look specifically for the part mentioning strike price
    if "in-the-money (" in summary:
        print("\nFound strike price format in output.")
        # Extract the strike price value
        start_idx = summary.find("in-the-money (") + len("in-the-money (")
        end_idx = summary.find(")", start_idx)
        if start_idx > 0 and end_idx > 0:
            strike_price = summary[start_idx:end_idx]
            print(f"Extracted strike price: {strike_price}")
            
            # Verify it's a number, not a ticker
            try:
                float_value = float(strike_price)
                print(f"Strike price is correctly formatted as a number: {float_value:.2f}")
            except ValueError:
                print(f"WARNING: Strike price is not a number: '{strike_price}'")
                if "$" in strike_price or ticker in strike_price:
                    print("ERROR: Strike price still contains ticker symbol!")
    else:
        print("\nWARNING: Could not find 'in-the-money (...)' in the output.")

if __name__ == "__main__":
    # Test with TSLA
    test_unusual_activity("TSLA")
    
    # Uncomment to test with other tickers
    # test_unusual_activity("AAPL")
    # test_unusual_activity("AMZN")
    # test_unusual_activity("NVDA")