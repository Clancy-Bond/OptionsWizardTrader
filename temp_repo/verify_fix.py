"""
Verify that our fixes to the stop loss system are working properly.
"""
import yfinance as yf
from technical_analysis import get_stop_loss_recommendations
import json

def main():
    # Test with the same parameters that caused the error
    print("Testing TSLA stop loss recommendation (swing trade horizon)...")
    ticker = "TSLA"
    current_price = 221.86
    option_type = "call"
    expiration_date = "2025-05-02"
    
    # Get the recommendation
    result = get_stop_loss_recommendations(ticker, current_price, option_type, expiration_date)
    
    # Print the keys in the result
    print(f"Result keys: {list(result.keys())}")
    
    # Check if 'trade_horizon' key exists
    if 'trade_horizon' in result:
        print(f"Trade horizon: {result['trade_horizon']}")
    else:
        print("Error: 'trade_horizon' key is missing")
    
    # Print out the recommendation if available
    if 'swing' in result:
        stop_level = result['swing']['level']
        print(f"Swing stop level: ${stop_level:.2f}")
        # Calculate the buffer percentage
        buffer_percentage = ((current_price - stop_level) / current_price * 100) if option_type.lower() == 'call' else ((stop_level - current_price) / current_price * 100)
        print(f"Buffer percentage: {buffer_percentage:.2f}%")
        
        # Print a snippet of the recommendation
        recommendation = result['swing']['recommendation']
        print(f"Recommendation snippet: {recommendation[:100]}...")
    else:
        print("Error: 'swing' key is missing or null")
        
    # Also try with an SPY call (1 DTE to test buffer limits)
    print("\nTesting SPY stop loss recommendation (scalp trade horizon)...")
    spy_ticker = "SPY"
    spy_price = 496.48
    spy_option_type = "call"
    spy_expiration = "2025-04-09"  # 1 day out
    
    # Get the recommendation
    spy_result = get_stop_loss_recommendations(spy_ticker, spy_price, spy_option_type, spy_expiration)
    
    # Print the keys in the result
    print(f"SPY result keys: {list(spy_result.keys())}")
    
    # Print out the recommendation if available
    if 'scalp' in spy_result:
        stop_level = spy_result['scalp']['level']
        print(f"Scalp stop level: ${stop_level:.2f}")
        # Calculate the buffer percentage
        buffer_percentage = ((spy_price - stop_level) / spy_price * 100)
        print(f"Buffer percentage: {buffer_percentage:.2f}%")
        
        # Check if it's within the 1% limit for 1 DTE
        if buffer_percentage <= 1.0:
            print("✓ Buffer is correctly limited to 1.0% for 1 DTE")
        else:
            print(f"× Buffer exceeds 1.0% limit for 1 DTE: {buffer_percentage:.2f}%")
        
        # Print a snippet of the recommendation
        recommendation = spy_result['scalp']['recommendation']
        print(f"Recommendation snippet: {recommendation[:100]}...")
    else:
        print("Error: 'scalp' key is missing or null")
    
    return result, spy_result

if __name__ == "__main__":
    main()