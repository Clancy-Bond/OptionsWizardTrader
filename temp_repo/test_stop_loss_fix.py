"""
Test script to verify our fixes for the primary key error
and buffer enforcement in the stop loss system.
"""
import yfinance as yf
from technical_analysis import get_stop_loss_recommendation

def test_stop_loss_with_tesla():
    """
    Test the stop loss recommendation with TSLA, which previously triggered the error.
    Testing the same parameters that caused the error in the logs:
    - TSLA calls with expiration date of 2025-05-02 (swing trade horizon)
    """
    print("Testing TSLA stop loss recommendation with expiration 2025-05-02...")
    
    # Get current TSLA price
    tsla = yf.Ticker("TSLA")
    current_price = tsla.info.get('currentPrice', tsla.history(period='1d')['Close'].iloc[-1])
    print(f"TSLA Current Price: ${current_price:.2f}")
    
    # Get stop loss recommendations
    result = get_stop_loss_recommendation(tsla, current_price, 'call', '2025-05-02')
    
    # Check if 'primary' key exists
    print(f"Primary key exists: {'primary' in result}")
    
    # Print the stop loss level
    if 'primary' in result:
        print(f"Primary stop level: ${result['primary']['level']:.2f}")
        print(f"Trade horizon: {result['trade_horizon']}")
        
        # Print a snippet of the recommendation
        recommendation = result['primary']['recommendation']
        print(f"Recommendation snippet: {recommendation[:100]}...")
    else:
        print("Error: 'primary' key is still missing!")
        
    # Print all keys in the result
    print(f"Result keys: {list(result.keys())}")
    
    # Print the swing recommendation separately
    if 'swing' in result:
        print(f"\nSwing stop level: ${result['swing']['level']:.2f}")
        
    return result

if __name__ == "__main__":
    test_stop_loss_with_tesla()