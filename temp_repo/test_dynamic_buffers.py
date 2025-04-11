"""
Test script to verify that dynamic buffers are working correctly based on days to expiration.
This will test different expiration dates for scalp, swing, and longterm trades.
"""

import yfinance as yf
import datetime
from technical_analysis import get_stop_loss_recommendations

def test_buffer_sizes():
    """
    Test the buffer sizes for different expiration dates.
    """
    ticker_symbol = "SPY"
    current_price = 500.0
    
    # Test various expiration dates (0, 1, 2, 5, 14, 30, 90, 180 days from now)
    today = datetime.datetime.now().date()
    expiration_dates = [
        (today + datetime.timedelta(days=0)).strftime("%Y-%m-%d"),  # Today
        (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),  # Tomorrow
        (today + datetime.timedelta(days=2)).strftime("%Y-%m-%d"),  # 2 days
        (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),  # 5 days
        (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), # 14 days
        (today + datetime.timedelta(days=30)).strftime("%Y-%m-%d"), # 30 days
        (today + datetime.timedelta(days=90)).strftime("%Y-%m-%d"), # 90 days
        (today + datetime.timedelta(days=180)).strftime("%Y-%m-%d") # 180 days
    ]
    
    print("\n===== TESTING CALL OPTIONS =====")
    for expiration in expiration_dates:
        days_to_exp = (datetime.datetime.strptime(expiration, "%Y-%m-%d").date() - today).days
        print(f"\nTesting {ticker_symbol} CALL with {days_to_exp} days to expiration ({expiration}):")
        try:
            # Pass the expiration date string, not days_to_expiration
            results = get_stop_loss_recommendations(ticker_symbol, current_price, "call", expiration)
            
            trade_horizon = results["trade_horizon"]
            print(f"• Trade horizon: {trade_horizon}")
            
            if "scalp" in results:
                scalp = results["scalp"]
                scalp_level = scalp["level"]
                scalp_drop_pct = ((current_price - scalp_level) / current_price) * 100
                print(f"• Scalp stop: ${scalp_level:.2f} ({scalp_drop_pct:.1f}% buffer)")
            
            if "swing" in results:
                swing = results["swing"]
                swing_level = swing["level"]
                swing_drop_pct = ((current_price - swing_level) / current_price) * 100
                print(f"• Swing stop: ${swing_level:.2f} ({swing_drop_pct:.1f}% buffer)")
            
            if "longterm" in results:
                longterm = results["longterm"]
                longterm_level = longterm["level"]
                longterm_drop_pct = ((current_price - longterm_level) / current_price) * 100
                print(f"• Longterm stop: ${longterm_level:.2f} ({longterm_drop_pct:.1f}% buffer)")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\n===== TESTING PUT OPTIONS =====")
    for expiration in expiration_dates:
        days_to_exp = (datetime.datetime.strptime(expiration, "%Y-%m-%d").date() - today).days
        print(f"\nTesting {ticker_symbol} PUT with {days_to_exp} days to expiration ({expiration}):")
        try:
            # Pass the expiration date string, not days_to_expiration
            results = get_stop_loss_recommendations(ticker_symbol, current_price, "put", expiration)
            
            trade_horizon = results["trade_horizon"]
            print(f"• Trade horizon: {trade_horizon}")
            
            if "scalp" in results:
                scalp = results["scalp"]
                scalp_level = scalp["level"]
                scalp_rise_pct = ((scalp_level - current_price) / current_price) * 100
                print(f"• Scalp stop: ${scalp_level:.2f} ({scalp_rise_pct:.1f}% buffer)")
            
            if "swing" in results:
                swing = results["swing"]
                swing_level = swing["level"]
                swing_rise_pct = ((swing_level - current_price) / current_price) * 100
                print(f"• Swing stop: ${swing_level:.2f} ({swing_rise_pct:.1f}% buffer)")
            
            if "longterm" in results:
                longterm = results["longterm"]
                longterm_level = longterm["level"]
                longterm_rise_pct = ((longterm_level - current_price) / current_price) * 100
                print(f"• Longterm stop: ${longterm_level:.2f} ({longterm_rise_pct:.1f}% buffer)")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_buffer_sizes()