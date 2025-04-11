"""
A focused test for the dynamic buffer sizes in stop loss calculations.
This directly calls the technical_analysis.py functions to verify buffer sizes.
"""

import datetime
import numpy as np
from technical_analysis import (
    get_scalp_stop_loss, 
    get_swing_stop_loss, 
    get_longterm_stop_loss
)

def test_buffer_sizes():
    """
    Test the buffer sizes for different days to expiration (DTE) to verify
    they're properly scaling based on our dynamic buffer implementation.
    """
    # Test parameters
    current_price = 500.0
    ticker = "SPY"
    option_type = "call"
    
    # Test cases for different days to expiration
    dte_values = [0, 1, 2, 3, 5, 7, 14, 30, 90, 180]
    
    # Test the scalp stop loss function (should use 0.1% for 0-1 DTE, 0.2% for 2 DTE)
    print("\n===== SCALP STOP LOSS BUFFERS =====")
    for dte in dte_values:
        try:
            stop_level = get_scalp_stop_loss(ticker, current_price, option_type, dte)
            if option_type == "call":
                buffer_pct = ((current_price - stop_level) / current_price) * 100
                print(f"• DTE {dte}: Stop level ${stop_level:.2f} ({buffer_pct:.1f}% below current price)")
            else:
                buffer_pct = ((stop_level - current_price) / current_price) * 100
                print(f"• DTE {dte}: Stop level ${stop_level:.2f} ({buffer_pct:.1f}% above current price)")
        except Exception as e:
            print(f"• DTE {dte}: Error - {str(e)}")
    
    # Test the swing stop loss function (should use 3% for 3-5 DTE, 5% for longer)
    print("\n===== SWING STOP LOSS BUFFERS =====")
    for dte in dte_values:
        try:
            stop_level = get_swing_stop_loss(ticker, current_price, option_type, dte)
            if option_type == "call":
                buffer_pct = ((current_price - stop_level) / current_price) * 100
                print(f"• DTE {dte}: Stop level ${stop_level:.2f} ({buffer_pct:.1f}% below current price)")
            else:
                buffer_pct = ((stop_level - current_price) / current_price) * 100
                print(f"• DTE {dte}: Stop level ${stop_level:.2f} ({buffer_pct:.1f}% above current price)")
        except Exception as e:
            print(f"• DTE {dte}: Error - {str(e)}")
    
    # Test the longterm stop loss function (should use a larger buffer)
    print("\n===== LONGTERM STOP LOSS BUFFERS =====")
    for dte in dte_values:
        try:
            stop_level = get_longterm_stop_loss(ticker, current_price, option_type, dte)
            if option_type == "call":
                buffer_pct = ((current_price - stop_level) / current_price) * 100
                print(f"• DTE {dte}: Stop level ${stop_level:.2f} ({buffer_pct:.1f}% below current price)")
            else:
                buffer_pct = ((stop_level - current_price) / current_price) * 100
                print(f"• DTE {dte}: Stop level ${stop_level:.2f} ({buffer_pct:.1f}% above current price)")
        except Exception as e:
            print(f"• DTE {dte}: Error - {str(e)}")
    
    # Test put options as well
    option_type = "put"
    print("\n===== PUT OPTION BUFFERS =====")
    for dte in [1, 5, 30]:
        try:
            scalp_level = get_scalp_stop_loss(ticker, current_price, option_type, dte)
            swing_level = get_swing_stop_loss(ticker, current_price, option_type, dte)
            longterm_level = get_longterm_stop_loss(ticker, current_price, option_type, dte)
            
            # Calculate buffer percentages
            scalp_buffer = ((scalp_level - current_price) / current_price) * 100
            swing_buffer = ((swing_level - current_price) / current_price) * 100
            longterm_buffer = ((longterm_level - current_price) / current_price) * 100
            
            print(f"\nDTE {dte}:")
            print(f"• Scalp stop: ${scalp_level:.2f} ({scalp_buffer:.1f}% above current price)")
            print(f"• Swing stop: ${swing_level:.2f} ({swing_buffer:.1f}% above current price)")
            print(f"• Longterm stop: ${longterm_level:.2f} ({longterm_buffer:.1f}% above current price)")
        except Exception as e:
            print(f"DTE {dte}: Error - {str(e)}")

if __name__ == "__main__":
    test_buffer_sizes()