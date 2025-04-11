"""
Verify that technical support levels are correctly displayed in the stop loss recommendations.
This script specifically checks that when technical support levels are found within buffer limits,
those actual percentages are shown rather than the maximum buffer percentage.
"""

import yfinance as yf
import numpy as np
import datetime
from technical_analysis import get_stop_loss_recommendations

def test_technical_stop_display():
    """
    Test a set of stocks, option types, and DTEs to verify the technical stop display
    is showing the actual technical support level percentage rather than the maximum buffer.
    """
    print("Testing Technical Stop Level Display")
    print("===================================")
    print()
    
    # Test stock symbols to check
    test_cases = [
        # Stock, Option Type, DTE, Description
        ("TSLA", "call", 25, "TSLA 25-day CALL (should use actual technical level if < 5%)"),
        ("AAPL", "call", 15, "AAPL 15-day CALL (should use actual technical level if < 5%)"),
        ("SPY", "put", 5, "SPY 5-day PUT (should use actual technical level if < 3%)"),
        ("QQQ", "put", 2, "QQQ 2-day PUT (should use actual technical level if < 2%)")
    ]
    
    for ticker, option_type, dte, description in test_cases:
        print(f"\n[{description}]")
        
        try:
            # Get stock data
            stock = yf.Ticker(ticker)
            current_price = stock.history(period="1d")["Close"].iloc[-1]
            
            # Calculate expiration date based on DTE
            expiration_date = (datetime.datetime.now() + datetime.timedelta(days=dte)).strftime("%Y-%m-%d")
            
            print(f"Current price: ${current_price:.2f}")
            print(f"Days to expiration: {dte}")
            
            # Get max buffer based on DTE for comparison
            if dte <= 1:
                max_buffer = 1.0  # 1% for 0-1 DTE
            elif dte <= 2:
                max_buffer = 2.0  # 2% for 2 DTE
            elif dte <= 5:
                max_buffer = 3.0  # 3% for 3-5 DTE
            elif dte <= 60:
                max_buffer = 5.0  # 5% for medium-term
            else:
                max_buffer = 7.0 if option_type.lower() == 'put' else 5.0  # 7% for long-term puts, 5% for calls
            
            print(f"Maximum buffer limit for {dte} DTE {option_type}: {max_buffer:.1f}%")
            
            # Get stop loss recommendations
            result = get_stop_loss_recommendations(ticker, current_price, option_type, expiration_date)
            
            # Extract the primary recommendation
            if "primary" in result:
                stop_level = result["primary"].get("level", 0.0)
            else:
                # Use appropriate time horizon based on DTE
                if dte <= 2:
                    stop_level = result.get("scalp", {}).get("level", 0.0)
                elif dte <= 60:
                    stop_level = result.get("swing", {}).get("level", 0.0)
                else:
                    stop_level = result.get("longterm", {}).get("level", 0.0)
            
            # Calculate actual buffer percentage
            if option_type.lower() == "call":
                actual_buffer = (current_price - stop_level) / current_price * 100
            else:
                actual_buffer = (stop_level - current_price) / current_price * 100
                
            print(f"Technical stop level: ${stop_level:.2f}")
            print(f"Actual buffer: {actual_buffer:.2f}%")
            
            # Check if it's using the maximum buffer (within 0.1% of max)
            if abs(actual_buffer - max_buffer) < 0.1:
                print("✓ Using maximum buffer (technical level at or beyond max)")
            elif actual_buffer < max_buffer:
                print("✓ Using technical level (within buffer limits)")
            else:
                print("❌ Buffer exceeds maximum limit, this is a BUG!")
                
        except Exception as e:
            print(f"Error testing {ticker} {option_type}: {e}")

if __name__ == "__main__":
    test_technical_stop_display()