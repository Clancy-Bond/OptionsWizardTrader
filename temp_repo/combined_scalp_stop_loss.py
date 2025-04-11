"""
Combined stop-loss strategy for short-term/scalp trades (2DTE or less),
comparing wick-based and VWAP-based stop loss levels.

This module implements two technical stop-loss strategies:
1. Wick-based stops: Using the lowest/highest wicks of recent candles
2. VWAP-based stops: Using VWAP as a technical boundary

For each strategy, it calculates a stop-loss level, then compares them
to determine which one is tighter (closer to entry).
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

def calculate_vwap(data):
    """
    Calculate VWAP (Volume Weighted Average Price)
    
    Args:
        data: DataFrame with OHLCV data
        
    Returns:
        Current VWAP value
    """
    # Calculate typical price for each candle
    data['TypicalPrice'] = (data['High'] + data['Low'] + data['Close']) / 3
    
    # Calculate VWAP components
    data['PriceVolume'] = data['TypicalPrice'] * data['Volume']
    data['CumulativePriceVolume'] = data['PriceVolume'].cumsum()
    data['CumulativeVolume'] = data['Volume'].cumsum()
    
    # Calculate VWAP
    data['VWAP'] = data['CumulativePriceVolume'] / data['CumulativeVolume']
    
    # Return the most recent VWAP value
    return data['VWAP'].iloc[-1]

def get_wick_based_stop(data, option_type, atr=None, lookback_candles=3):
    """
    Calculate stop loss based on recent candle wicks with optional ATR buffer
    
    Args:
        data: DataFrame with OHLCV data
        option_type: 'call' or 'put'
        atr: Optional ATR value for buffer calculation
        lookback_candles: Number of recent candles to consider (default: 3)
        
    Returns:
        Stop loss price level
    """
    # Use only recent candles based on lookback parameter
    recent_data = data.tail(lookback_candles)
    
    # For call options (long trades): find lowest wick
    if option_type.lower() == 'call':
        lowest_wick = recent_data['Low'].min()
        
        # ATR buffer removed
        buffer = 0  # No buffer
        stop_loss = lowest_wick - buffer
        
    # For put options (short trades): find highest wick
    else:
        highest_wick = recent_data['High'].max()
        
        # ATR buffer removed
        buffer = 0  # No buffer
        stop_loss = highest_wick + buffer
    
    return stop_loss

def get_vwap_based_stop(data, option_type, current_price):
    """
    Calculate stop loss based on VWAP level
    
    Args:
        data: DataFrame with OHLCV data
        option_type: 'call' or 'put'
        current_price: Current stock price
        
    Returns:
        VWAP-based stop loss level and a flag indicating if candle close is required,
        plus a validity flag (False if VWAP is not a valid stop position)
    """
    # Calculate VWAP
    vwap = calculate_vwap(data)
    
    # For call options: stop if close below VWAP
    if option_type.lower() == 'call':
        # For calls, VWAP should be below current price to be a valid stop
        if vwap < current_price:
            stop_level = vwap
            is_valid = True
        else:
            # If VWAP is above current price, it's not valid as a stop loss
            stop_level = vwap  # Return the actual VWAP still for reference
            is_valid = False
    # For put options: stop if close above VWAP
    else:
        # For puts, VWAP should be above current price to be a valid stop
        if vwap > current_price:
            stop_level = vwap
            is_valid = True
        else:
            # If VWAP is below current price, it's not valid as a stop loss
            stop_level = vwap  # Return the actual VWAP still for reference
            is_valid = False
    
    # Return the stop level, a flag to indicate this requires a candle close, and validity
    return stop_level, True, is_valid  # True indicates this requires a candle close confirmation

def calculate_stop_distance(current_price, stop_level, option_type):
    """
    Calculate the distance between current price and stop level in dollar terms
    
    Args:
        current_price: Current stock price
        stop_level: Stop loss level
        option_type: 'call' or 'put'
        
    Returns:
        Absolute distance in dollars (positive value)
    """
    if option_type.lower() == 'call':
        # For calls, stop is below current price
        return abs(current_price - stop_level)
    else:
        # For puts, stop is above current price
        return abs(stop_level - current_price)

def get_combined_scalp_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate combined stop loss for scalp/day trades (2DTE or less) using both
    wick-based and VWAP-based methods. Returns the tighter (closer) stop level.
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        days_to_expiration: Days to option expiration
        trade_type: Override the default trade type determination
    
    Returns:
        Dictionary with stop loss recommendation
    """
    try:
        # Only apply this logic for scalp trades with 2 DTE or less
        if days_to_expiration is not None and days_to_expiration > 2:
            raise ValueError("Combined stop loss is only for 2DTE or less")
        
        # Try to get 5-minute data first (last 2 days is usually sufficient for scalp)
        hist_data_5m = stock.history(period="2d", interval="5m")
        
        # Also get 15-minute data for confirmation
        hist_data_15m = stock.history(period="2d", interval="15m")
        
        # If 5m or 15m data isn't available, fall back to 1h data
        if hist_data_5m.empty or hist_data_5m.shape[0] < 10:
            hist_data = stock.history(period="3d", interval="1h")
            timeframe = "1h" 
        else:
            # 5-minute data will be our primary timeframe
            hist_data = hist_data_5m
            timeframe = "5m"
        
        # Calculate ATR for volatility-based buffer
        from technical_analysis import calculate_atr
        atr = calculate_atr(hist_data, window=7, trade_type=trade_type)  # 7-period ATR for scalp trades
        
        # Calculate both stop loss methods
        wick_stop = get_wick_based_stop(hist_data, option_type, atr, lookback_candles=3)
        vwap_stop, requires_candle_close, vwap_is_valid = get_vwap_based_stop(hist_data, option_type, current_price)
        
        # Calculate DTE-based maximum buffer percentage for CALL options
        max_buffer_pct = 0.05  # Default 5% maximum
        if days_to_expiration is not None and option_type.lower() == 'call':
            if days_to_expiration <= 1:
                max_buffer_pct = 0.01  # 1% for 0-1 DTE
            elif days_to_expiration <= 2:
                max_buffer_pct = 0.02  # 2% for 2 DTE
            elif days_to_expiration <= 5:
                max_buffer_pct = 0.03  # 3% for 3-5 DTE
            
        # Calculate max allowed stop level for CALL options based on buffer percentage
        min_allowed_stop = current_price * (1 - max_buffer_pct) if option_type.lower() == 'call' else 0
        
        # If VWAP is not a valid stop (wrong side of price), always use wick-based stop
        if not vwap_is_valid:
            stop_loss = wick_stop
            stop_method = "wick-based"
            requires_close = False
            print(f"VWAP at {vwap_stop:.2f} is not valid as stop for {option_type} option with current price {current_price:.2f}, using wick-based stop at {wick_stop:.2f}")
        else:
            # Calculate distance from current price for each method
            wick_distance = calculate_stop_distance(current_price, wick_stop, option_type)
            vwap_distance = calculate_stop_distance(current_price, vwap_stop, option_type)
            
            # Choose the tighter stop (closer to current price)
            if wick_distance <= vwap_distance:
                stop_loss = wick_stop
                stop_method = "wick-based"
                requires_close = False
            else:
                stop_loss = vwap_stop
                stop_method = "VWAP-based"
                requires_close = requires_candle_close
        
        # For CALL options, ensure we don't exceed the maximum buffer
        if option_type.lower() == 'call' and stop_loss < min_allowed_stop:
            # Technical stop exceeds maximum buffer, so cap it
            stop_loss = min_allowed_stop
            stop_method = f"{stop_method} (capped at {max_buffer_pct*100:.1f}% max)"
            print(f"Stop loss for {option_type} option capped at ${stop_loss:.2f} ({max_buffer_pct*100:.1f}% max buffer)")
            
        # Calculate percentage change for display
        if option_type.lower() == 'call':
            percentage_change = ((current_price - stop_loss) / current_price) * 100
            direction_text = "below"
        else:
            percentage_change = ((stop_loss - current_price) / current_price) * 100
            direction_text = "above"
            
        # Create descriptive text about the method used
        method_description = f"{stop_method.capitalize()} stop ({timeframe} chart)"
        
        # Add candle close requirement text if needed
        close_requirement = ""
        if requires_close:
            close_requirement = f"\n⚠️ **Requires a full candle close {direction_text} VWAP to trigger**"
            
        # Create recommendation text with the same formatting as before
        recommendation = (
            f"⚡ **SCALP TRADE STOP LOSS ({timeframe}-chart)** ⚡\n\n"
            f"• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_change:.1f}% {direction_text} current price)\n"
            f"• Based on {method_description}"
            f"{close_requirement}"
        )
        
        # Return the result in the same format as the original get_scalp_stop_loss
        return {
            "level": stop_loss,
            "recommendation": recommendation,
            "time_horizon": "scalp",
            "option_stop_price": current_price * 0.5,  # Simplified estimation
            "requires_candle_close": requires_close,
            "method": stop_method
        }
            
    except Exception as e:
        print(f"Error calculating combined scalp stop loss: {str(e)}")
        
        # Fallback to simple percentage based on option type and DTE
        if option_type.lower() == 'call':
            # Use tighter stop for very short-dated options
            if days_to_expiration is not None and days_to_expiration <= 1:
                buffer_percentage = 0.99  # 1% for 0-1 DTE
            else:
                buffer_percentage = 0.98  # 2% for 2 DTE
                
            stop_loss = current_price * buffer_percentage
            percentage_drop = (1 - buffer_percentage) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min)** ⚡\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Standard scalp-trade protection level (fallback method)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5,
                "requires_candle_close": False,
                "method": "percentage-based (fallback)"
            }
        else:
            # Use tighter stop for very short-dated options
            if days_to_expiration is not None and days_to_expiration <= 1:
                buffer_percentage = 1.01  # 1% for 0-1 DTE
            else:
                buffer_percentage = 1.02  # 2% for 2 DTE
                
            stop_loss = current_price * buffer_percentage
            percentage_rise = (buffer_percentage - 1) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min)** ⚡\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Standard scalp-trade protection level (fallback method)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5,
                "requires_candle_close": False,
                "method": "percentage-based (fallback)"
            }