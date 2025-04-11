"""
Test script to verify the fix for passing expiration date correctly
between discord_bot.py and technical_analysis.py
"""

import os
import sys
import yfinance as yf
from technical_analysis import get_stop_loss_recommendations

def test_expiry_param():
    """
    Test that get_stop_loss_recommendations correctly handles expiration_date as a string
    """
    print("Testing expiration date string handling...")
    
    # Test parameters
    ticker_symbol = "AAPL"
    current_price = 175.75
    option_type = "call"
    expiration_date = "2025-05-16"  # A date string in YYYY-MM-DD format
    
    # Call the function with the expiration date string
    print(f"Calling get_stop_loss_recommendations with: {ticker_symbol}, {current_price}, {option_type}, {expiration_date}")
    result = get_stop_loss_recommendations(ticker_symbol, current_price, option_type, expiration_date)
    
    # Print the results
    print("\nResults:")
    print(f"Trade horizon: {result.get('trade_horizon', 'Not found')}")
    
    # Check each time horizon
    for horizon in ['scalp', 'swing', 'longterm']:
        if horizon in result:
            print(f"\n{horizon.upper()} recommendation:")
            horizon_data = result[horizon]
            print(f"  Stop level: ${horizon_data.get('level', 'Not found')}")
            print(f"  Option stop price: ${horizon_data.get('option_stop_price', 'Not found')}")
    
    print("\nTest completed!")
    
if __name__ == "__main__":
    test_expiry_param()