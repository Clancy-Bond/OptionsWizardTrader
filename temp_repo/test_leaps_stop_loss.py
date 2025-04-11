#!/usr/bin/env python3

"""
Test script for the LEAPS weekly-based stop loss
"""

import yfinance as yf
from technical_analysis import get_stop_loss_recommendation

def test_leaps_stop_loss():
    """
    Test the LEAPS weekly-based stop loss functionality.
    """
    # Test with a common stock that has options (SPY)
    ticker_symbol = 'SPY'
    stock = yf.Ticker(ticker_symbol)
    current_price = stock.history(period="1d")['Close'].iloc[-1]
    
    print(f"Testing LEAPS stop loss for {ticker_symbol} at current price ${current_price:.2f}")
    
    # Test with both call and put options
    for option_type in ['call', 'put']:
        print(f"\nTesting {option_type.upper()} option type:")
        
        # Test with medium-term (not LEAPS)
        result_medium = get_stop_loss_recommendation(stock, current_price, option_type, "2025-06-20")
        if "leaps_weekly" in result_medium:
            print("ERROR: LEAPS weekly stop loss was incorrectly applied to medium-term option")
        else:
            print("✓ Medium-term option (< 180 DTE) does NOT use LEAPS weekly approach")
        
        # Test with LEAPS (365+ days)
        result_leaps = get_stop_loss_recommendation(stock, current_price, option_type, "2026-06-19")
        if "leaps_weekly" in result_leaps:
            print(f"✓ LEAPS weekly stop loss successfully applied to long-term option")
            print(f"  - Stop level: ${result_leaps['leaps_weekly']['level']:.2f}")
            if "recommendation" in result_leaps['leaps_weekly']:
                print(f"  - Recommendation: {result_leaps['leaps_weekly']['recommendation']}")
            if result_leaps.get('primary') == result_leaps.get('leaps_weekly'):
                print("✓ LEAPS weekly correctly set as primary recommendation")
            else:
                print("ERROR: LEAPS weekly is not set as primary recommendation")
        else:
            print("ERROR: LEAPS weekly stop loss was NOT applied to long-term option")

if __name__ == "__main__":
    test_leaps_stop_loss()