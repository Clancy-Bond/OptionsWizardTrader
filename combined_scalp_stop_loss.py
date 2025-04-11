import yfinance as yf
import pandas as pd
import numpy as np

def calculate_scalp_stop_loss(ticker, option_type):
    """
    Calculate stop-loss level for scalp trades using a combined approach
    of wick-based and VWAP-based methods
    
    Args:
        ticker (str): The ticker symbol
        option_type (str): 'call' or 'put'
    
    Returns:
        float: The stop-loss price level for the underlying stock
    """
    # Get intraday data (5 minute candles) for the past day
    data = yf.download(ticker, period='1d', interval='5m', progress=False)
    
    if data.empty:
        raise ValueError(f"No data available for {ticker}")
    
    # Calculate wick-based stop loss
    if option_type == 'call':
        # For calls, look at recent lows
        recent_candles = data.tail(5)  # Last 5 candles (25 minutes)
        lowest_wick = recent_candles['Low'].min()
        wick_stop = lowest_wick
    else:
        # For puts, look at recent highs
        recent_candles = data.tail(5)  # Last 5 candles (25 minutes)
        highest_wick = recent_candles['High'].max()
        wick_stop = highest_wick
    
    # Calculate VWAP
    v = data['Volume']
    tp = (data['Close'] + data['Low'] + data['High']) / 3
    vwap = (tp * v).cumsum() / v.cumsum()
    current_vwap = vwap.iloc[-1]
    
    # Determine VWAP-based stop
    if option_type == 'call':
        # For calls, stop is below VWAP
        vwap_stop = current_vwap * 0.995  # Slightly below VWAP
    else:
        # For puts, stop is above VWAP
        vwap_stop = current_vwap * 1.005  # Slightly above VWAP
    
    # Return the tighter of the two stops
    current_price = data['Close'].iloc[-1]
    
    if option_type == 'call':
        # For calls, we want the higher (closer to current price) of the two stops
        stop_loss = max(wick_stop, vwap_stop)
        
        # But ensure stop isn't too close to current price (minimum 0.5% buffer)
        min_buffer = current_price * 0.995
        stop_loss = min(stop_loss, min_buffer)
    else:
        # For puts, we want the lower (closer to current price) of the two stops
        stop_loss = min(wick_stop, vwap_stop)
        
        # But ensure stop isn't too close to current price (minimum 0.5% buffer)
        min_buffer = current_price * 1.005
        stop_loss = max(stop_loss, min_buffer)
    
    return stop_loss
