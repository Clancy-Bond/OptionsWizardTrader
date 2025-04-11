"""
Test script to verify the dynamic buffer changes for stop loss calculations.

This creates a simple test case that directly calls the get_scalp_stop_loss 
and get_swing_stop_loss functions with different days_to_expiration values
to verify that the appropriate buffer sizes are being used and correctly
displayed in the recommendation text.
"""

import sys
from technical_analysis import get_scalp_stop_loss, get_swing_stop_loss
import yfinance as yf

def test_dynamic_buffers():
    """Test the dynamic buffers for different days_to_expiration values"""
    print("===== TESTING DYNAMIC BUFFERS =====")
    
    # Get a sample stock
    ticker_symbol = 'TSLA'
    try:
        stock = yf.Ticker(ticker_symbol)
        current_price = stock.history(period="1d")['Close'].iloc[-1]
        print(f"Current price for {ticker_symbol}: ${current_price:.2f}")
    except Exception as e:
        print(f"Error getting stock data: {e}")
        return
        
    # Test for different days to expiration
    dte_values = [0, 1, 2, 3, 5, 10, 30]
    
    print("\n== TESTING CALL OPTIONS ==")
    for days_to_expiration in dte_values:
        print(f"\nTesting with DTE = {days_to_expiration}:")
        
        # Test scalp trade stop loss
        scalp_result = get_scalp_stop_loss(stock, current_price, "call", days_to_expiration)
        scalp_level = scalp_result.get('level')
        scalp_percentage = ((current_price - scalp_level) / current_price) * 100
        scalp_rec = scalp_result.get('recommendation')
        
        # Extract the displayed percentage from the recommendation text
        import re
        displayed_percentage = None
        match = re.search(r'\(([0-9.]+)% below', scalp_rec)
        if match:
            displayed_percentage = float(match.group(1))
        
        print(f"  Scalp stop loss: ${scalp_level:.2f} ({scalp_percentage:.1f}% below current)")
        print(f"  Displayed percentage: {displayed_percentage}")
        
        # Test swing trade stop loss
        swing_result = get_swing_stop_loss(stock, current_price, "call", days_to_expiration)
        swing_level = swing_result.get('level')
        swing_percentage = ((current_price - swing_level) / current_price) * 100
        swing_rec = swing_result.get('recommendation')
        
        # Extract the ATR multiple from the recommendation text
        atr_multiple = None
        match = re.search(r'volatility \(([0-9.]+)x ATR', swing_rec)
        if match:
            atr_multiple = float(match.group(1))
        
        print(f"  Swing stop loss: ${swing_level:.2f} ({swing_percentage:.1f}% below current)")
        if atr_multiple:
            print(f"  ATR multiple displayed: {atr_multiple}x")
        else:
            print("  No ATR multiple found in recommendation text")
    
    print("\n== TESTING PUT OPTIONS ==")
    for days_to_expiration in [0, 1, 3, 10]:
        print(f"\nTesting with DTE = {days_to_expiration}:")
        
        # Test scalp trade stop loss
        scalp_result = get_scalp_stop_loss(stock, current_price, "put", days_to_expiration)
        scalp_level = scalp_result.get('level')
        scalp_percentage = ((scalp_level - current_price) / current_price) * 100
        scalp_rec = scalp_result.get('recommendation')
        
        # Extract the displayed percentage from the recommendation text
        displayed_percentage = None
        match = re.search(r'\(([0-9.]+)% above', scalp_rec)
        if match:
            displayed_percentage = float(match.group(1))
        
        print(f"  Scalp stop loss: ${scalp_level:.2f} ({scalp_percentage:.1f}% above current)")
        print(f"  Displayed percentage: {displayed_percentage}")

if __name__ == '__main__':
    test_dynamic_buffers()