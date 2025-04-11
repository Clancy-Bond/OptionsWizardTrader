"""
Test script to verify which timeframes are available for SPY data
"""
import yfinance as yf

def check_timeframes():
    """Check which timeframes are available for SPY data"""
    print("Checking available timeframes for SPY...")
    
    # Get the stock data
    spy = yf.Ticker("SPY")
    
    # Check 5-minute data
    hist_data_5m = spy.history(period="2d", interval="5m")
    print(f"5-minute data: {'Available' if not hist_data_5m.empty else 'Not available'}")
    print(f"5-minute data shape: {hist_data_5m.shape[0] if not hist_data_5m.empty else 0} candles\n")
    
    # Check 15-minute data
    hist_data_15m = spy.history(period="2d", interval="15m")
    print(f"15-minute data: {'Available' if not hist_data_15m.empty else 'Not available'}")
    print(f"15-minute data shape: {hist_data_15m.shape[0] if not hist_data_15m.empty else 0} candles\n")
    
    # Check 1-hour data
    hist_data_1h = spy.history(period="3d", interval="1h")
    print(f"1-hour data: {'Available' if not hist_data_1h.empty else 'Not available'}")
    print(f"1-hour data shape: {hist_data_1h.shape[0] if not hist_data_1h.empty else 0} candles\n")
    
    # Verify the actual timeframe that would be used
    if not hist_data_5m.empty and hist_data_5m.shape[0] >= 10:
        print("The bot would use 5-minute data")
        timeframe = "5m"
        hist_data = hist_data_5m
    else:
        print("The bot would fall back to 1-hour data")
        timeframe = "1h"
        hist_data = hist_data_1h
    
    # Get VWAP value
    from combined_scalp_stop_loss import calculate_vwap
    try:
        vwap = calculate_vwap(hist_data)
        print(f"VWAP calculated on {timeframe} timeframe: ${vwap:.2f}")
    except Exception as e:
        print(f"Error calculating VWAP: {e}")
    
    # Get recent low value for wick-based stop
    if not hist_data.empty:
        recent_low = hist_data.tail(3)['Low'].min()
        print(f"Recent low (3 {timeframe} candles): ${recent_low:.2f}")

if __name__ == "__main__":
    check_timeframes()