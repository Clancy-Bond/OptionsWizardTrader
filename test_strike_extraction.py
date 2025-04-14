"""
Test the strike price extraction from option symbols
"""
import polygon_integration

def test_strike_extraction():
    """
    Test the extraction of strike prices from option symbols
    """
    # Test with various option symbols
    test_symbols = [
        "O:TSLA250417C00252500",  # TSLA $252.50 call expiring Apr 17, 2025
        "O:AAPL250418P00180000",  # AAPL $180.00 put expiring Apr 18, 2025
        "O:AMZN250425C00175000",  # AMZN $175.00 call expiring Apr 25, 2025
        "O:SPY250430P00530000",   # SPY $530.00 put expiring Apr 30, 2025
        "O:NVDA250502C01000000",  # NVDA $1000.00 call expiring May 2, 2025
    ]
    
    print("Testing strike price extraction from option symbols:")
    for symbol in test_symbols:
        strike = polygon_integration.extract_strike_from_symbol(symbol)
        print(f"{symbol} -> Strike price: {strike}")
    
    # Also test the get_simplified_unusual_activity_summary to ensure 
    # it dynamically shows the strike price
    print("\nTesting unusual activity summary for TSLA:")
    summary = polygon_integration.get_simplified_unusual_activity_summary("TSLA")
    print(summary)

if __name__ == "__main__":
    test_strike_extraction()