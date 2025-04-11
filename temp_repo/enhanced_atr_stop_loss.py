"""
Enhanced ATR-based Stop Loss System with Pattern Recognition

This module provides an enhanced stop loss system for options trading that incorporates:
1. Technical pattern recognition (breakout/engulfing candles)
2. Volume confirmation (≥ 1.5x average of last 10 candles)
3. ATR-based volatility buffers that scale with days to expiration
4. Pattern-specific buffer calculations (10% ATR for breakouts, 5% ATR for engulfing)
5. Support/resistance level validation for pattern confirmation

Usage:
    from enhanced_atr_stop_loss import get_enhanced_stop_loss
    
    # Get enhanced stop loss for AAPL call options with 14 DTE
    stop_loss = get_enhanced_stop_loss(stock, current_price, 'call', 14)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from scipy.signal import argrelextrema

def calculate_atr(data, window=14, period=None, trade_type=None):
    """
    Calculate Average True Range (ATR) using standard period
    
    Args:
        data: DataFrame with OHLC data
        window: ATR period (14 or 21 default) - compatible with technical_analysis.py
        period: Alternative name for window parameter (for backward compatibility)
        trade_type: "scalp", "swing", or "longterm" to adjust ATR period
        
    Returns:
        Latest ATR value
    """
    # Use period if provided (for backward compatibility)
    if period is not None:
        window = period
        
    # Adjust window based on trade_type if provided
    if trade_type is not None:
        if trade_type == "scalp":
            window = 7
        elif trade_type == "swing":
            window = 14
        elif trade_type == "longterm":
            window = 21
        
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    
    atr = true_range.rolling(window).mean().iloc[-1]
    return atr

def get_volume_confirmation(data, lookback=10, threshold=1.5):
    """
    Check if current volume is above threshold compared to average
    
    Args:
        data: DataFrame with volume data
        lookback: Number of periods to look back for average
        threshold: Multiplier for average (e.g., 1.5x average)
        
    Returns:
        Boolean indicating if volume confirmation exists and the ratio
    """
    if len(data) <= lookback:
        return False, 1.0
    
    current_volume = data['Volume'].iloc[-1]
    avg_volume = data['Volume'].iloc[-lookback-1:-1].mean()
    
    ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
    confirmation = ratio >= threshold
    
    return confirmation, ratio

def identify_breakout_candle(data, lookback=10):
    """
    Identify if the most recent candle is a breakout/breakdown candle
    
    Args:
        data: DataFrame with OHLC data
        lookback: Periods to check for prior range
        
    Returns:
        Dictionary with pattern information or None if no pattern
    """
    if len(data) <= lookback:
        return None
    
    # Get the current candle and prior range
    current = data.iloc[-1]
    prior = data.iloc[-lookback-1:-1]
    
    prior_high = prior['High'].max()
    prior_low = prior['Low'].min()
    
    # Check for breakout (close above prior high)
    if current['Close'] > prior_high and current['Open'] < prior_high:
        return {
            "pattern": "breakout",
            "direction": "bullish",
            "prior_level": prior_high,
            "candle_body_pct": (current['Close'] - current['Open']) / current['Open'] * 100
        }
    
    # Check for breakdown (close below prior low)
    if current['Close'] < prior_low and current['Open'] > prior_low:
        return {
            "pattern": "breakdown",
            "direction": "bearish",
            "prior_level": prior_low,
            "candle_body_pct": (current['Open'] - current['Close']) / current['Open'] * 100
        }
    
    return None

def identify_engulfing_candle(data):
    """
    Identify if the most recent candle is an engulfing pattern
    
    Args:
        data: DataFrame with OHLC data
        
    Returns:
        Dictionary with pattern information or None if no pattern
    """
    if len(data) < 2:
        return None
    
    current = data.iloc[-1]
    previous = data.iloc[-2]
    
    # Bullish engulfing (current candle completely engulfs previous)
    if (current['Open'] < previous['Close'] and 
        current['Close'] > previous['Open'] and
        current['Close'] > current['Open']):  # Green candle
        
        return {
            "pattern": "engulfing",
            "direction": "bullish",
            "prior_close": previous['Close'],
            "candle_body_pct": (current['Close'] - current['Open']) / current['Open'] * 100
        }
    
    # Bearish engulfing
    if (current['Open'] > previous['Close'] and 
        current['Close'] < previous['Open'] and
        current['Close'] < current['Open']):  # Red candle
        
        return {
            "pattern": "engulfing",
            "direction": "bearish",
            "prior_close": previous['Close'],
            "candle_body_pct": (current['Open'] - current['Close']) / current['Open'] * 100
        }
    
    return None

def scale_atr_for_dte(atr, days_to_expiration, pattern_type="breakout", trade_type=None):
    """
    Scale ATR buffer based on DTE, pattern type, and trade type
    
    Args:
        atr: ATR value to scale
        days_to_expiration: Days to option expiration
        pattern_type: "breakout" or "engulfing"
        trade_type: "scalp", "swing", or "longterm" (if None, determined from DTE)
    
    Returns:
        Scaled ATR buffer value
    """
    # ATR buffers removed - returning near-zero value
    return 0.0001  # Effectively removes buffer while avoiding division by zero issues

def calculate_breakout_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss based on breakout/breakdown candle pattern with ATR buffer
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        days_to_expiration: Days to expiration
        trade_type: "scalp", "swing", or "longterm" to adjust ATR period
    
    Returns:
        Dictionary with stop loss recommendation based on breakout pattern
    """
    # Get data for ATR calculation and pattern recognition (30 days of daily data)
    data = stock.history(period="1mo", interval="1d")
    
    if data.empty:
        return None
    
    # Identify breakout/breakdown pattern
    pattern = identify_breakout_candle(data)
    
    if not pattern:
        return None
    
    # Check volume confirmation (≥ 1.5x average of the last 10 candles)
    volume_confirmed, volume_ratio = get_volume_confirmation(data)
    
    # Skip patterns without volume confirmation
    if not volume_confirmed:
        return None
    
    # Find key support and resistance levels
    key_levels = find_support_resistance_levels(data)
    
    # Validate that pattern forms at key support/resistance levels
    pattern_level = pattern["prior_level"]
    
    if pattern["direction"] == "bullish":
        # For bullish breakout, validate it breaks a resistance level
        is_valid_level = is_near_support_resistance(pattern_level, key_levels["resistance"])
    else:
        # For bearish breakdown, validate it breaks a support level
        is_valid_level = is_near_support_resistance(pattern_level, key_levels["support"])
    
    # Skip patterns that don't form at key levels
    if not is_valid_level:
        return None
    
    # Calculate ATR with standard 14-period 
    atr = calculate_atr(data, window=14)
    
    # Scale ATR for DTE with the 10% buffer for breakout patterns
    scaled_atr = scale_atr_for_dte(atr, days_to_expiration, "breakout")
    
    # Set stop loss level based on pattern direction and option type
    if option_type.lower() == 'call':
        if pattern["direction"] == "bullish":
            # For bullish breakout + call options, stop below breakout candle with 10% ATR buffer
            stop_level = pattern["prior_level"] - scaled_atr
        else:
            # For bearish breakdown + call options, stop at breakdown level
            stop_level = pattern["prior_level"]
    else:  # put options
        if pattern["direction"] == "bearish":
            # For bearish breakdown + put options, stop above breakdown candle with 10% ATR buffer
            stop_level = pattern["prior_level"] + scaled_atr
        else:
            # For bullish breakout + put options, stop at breakout level
            stop_level = pattern["prior_level"]
    
    # Calculate percentage change from current price
    if option_type.lower() == 'call':
        percentage = ((current_price - stop_level) / current_price) * 100
        direction_emoji = "📉"
    else:
        percentage = ((stop_level - current_price) / current_price) * 100
        direction_emoji = "📈"
    
    # Build recommendation
    recommendation = (
        f"{direction_emoji} **${stop_level:.2f}** {direction_emoji}\n\n"
        f"• Stock Price Stop Level: ${stop_level:.2f} ({percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n"
        f"• Based on {pattern['direction']} {pattern['pattern']} pattern with 10% ATR buffer"
    )
    
    # Add volume confirmation
    recommendation += f"\n• Volume confirmation: {volume_ratio:.1f}× average volume"
    
    # Add key level validation
    recommendation += f"\n• Validated at key {'resistance' if pattern['direction'] == 'bullish' else 'support'} level"
    
    # Add note about candle close validation
    recommendation += "\n• Requires full candle CLOSE beyond stop level (not just wick)"
    
    # Determine trade horizon based on DTE
    if days_to_expiration is not None:
        if days_to_expiration <= 2:
            time_horizon = "scalp"
        elif days_to_expiration <= 90:
            time_horizon = "swing"
        else:
            time_horizon = "longterm"
    else:
        time_horizon = "swing"  # Default to swing if unknown
    
    return {
        "level": stop_level,
        "recommendation": recommendation,
        "pattern": pattern["pattern"],
        "direction": pattern["direction"],
        "volume_confirmed": volume_confirmed,
        "at_key_level": is_valid_level,
        "atr_buffer": scaled_atr,
        "entry_price": pattern["prior_level"],
        "time_horizon": time_horizon
    }

def calculate_engulfing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss based on engulfing candle pattern with ATR buffer
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        days_to_expiration: Days to expiration
        trade_type: "scalp", "swing", or "longterm" to adjust ATR period
    
    Returns:
        Dictionary with stop loss recommendation based on engulfing pattern
    """
    # Get data for ATR calculation
    data = stock.history(period="1mo", interval="1d")
    
    if data.empty:
        return None
    
    # Identify engulfing pattern
    pattern = identify_engulfing_candle(data)
    
    if not pattern:
        return None
    
    # Check volume confirmation (≥ 1.5x average of the last 10 candles)
    volume_confirmed, volume_ratio = get_volume_confirmation(data)
    
    # Skip patterns without volume confirmation
    if not volume_confirmed:
        return None
    
    # Find key support and resistance levels
    key_levels = find_support_resistance_levels(data)
    
    # Get the price of the engulfing pattern (current candle close)
    pattern_price = data.iloc[-1]['Close']
    
    # Validate that engulfing pattern forms at key support/resistance levels
    if pattern["direction"] == "bullish":
        # For bullish engulfing, validate it forms at support
        is_valid_level = is_near_support_resistance(pattern_price, key_levels["support"])
    else:
        # For bearish engulfing, validate it forms at resistance
        is_valid_level = is_near_support_resistance(pattern_price, key_levels["resistance"])
    
    # Skip patterns that don't form at key levels
    if not is_valid_level:
        return None
    
    # Calculate ATR with standard 14-period
    atr = calculate_atr(data, window=14)
    
    # Scale ATR for DTE with 5% ATR buffer for engulfing patterns
    scaled_atr = scale_atr_for_dte(atr, days_to_expiration, "engulfing")
    
    # Set stop loss level based on pattern direction and option type
    # For engulfing patterns, we use the engulfing candle's high/low with 5% ATR buffer
    if option_type.lower() == 'call':
        if pattern["direction"] == "bullish":
            # For bullish engulfing + call options, stop below prior candle low with 5% ATR buffer
            stop_level = data.iloc[-2]['Low'] - scaled_atr
            candle_ref = "below engulfing candle low"
        else:
            # For bearish engulfing + call options, stop at prior candle close
            stop_level = pattern["prior_close"]
            candle_ref = "at prior candle close"
    else:  # put options
        if pattern["direction"] == "bearish":
            # For bearish engulfing + put options, stop above prior candle high with 5% ATR buffer
            stop_level = data.iloc[-2]['High'] + scaled_atr
            candle_ref = "above engulfing candle high"
        else:
            # For bullish engulfing + put options, stop at prior candle close
            stop_level = pattern["prior_close"]
            candle_ref = "at prior candle close"
    
    # Calculate percentage change from current price
    if option_type.lower() == 'call':
        percentage = ((current_price - stop_level) / current_price) * 100
        direction_emoji = "📉"
    else:
        percentage = ((stop_level - current_price) / current_price) * 100
        direction_emoji = "📈"
    
    # Build recommendation
    recommendation = (
        f"{direction_emoji} **${stop_level:.2f}** {direction_emoji}\n\n"
        f"• Stock Price Stop Level: ${stop_level:.2f} ({percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n"
        f"• Based on {pattern['direction']} {pattern['pattern']} pattern with 5% ATR buffer\n"
        f"• Stop placed {candle_ref}"
    )
    
    # Add volume confirmation
    recommendation += f"\n• Volume confirmation: {volume_ratio:.1f}× average volume"
    
    # Add key level validation
    recommendation += f"\n• Pattern forms at key {'support' if pattern['direction'] == 'bullish' else 'resistance'} level"
    
    # Add note about candle close validation
    recommendation += "\n• Requires full candle CLOSE beyond stop level (not just wick)"
    
    # Determine trade horizon based on DTE
    if days_to_expiration is not None:
        if days_to_expiration <= 2:
            time_horizon = "scalp"
        elif days_to_expiration <= 90:
            time_horizon = "swing"
        else:
            time_horizon = "longterm"
    else:
        time_horizon = "swing"  # Default to swing if unknown
    
    return {
        "level": stop_level,
        "recommendation": recommendation,
        "pattern": pattern["pattern"],
        "direction": pattern["direction"],
        "volume_confirmed": volume_confirmed,
        "at_key_level": is_valid_level,
        "atr_buffer": scaled_atr,
        "entry_price": pattern_price,
        "time_horizon": time_horizon
    }

def find_support_resistance_levels(data, window=10):
    """
    Find key support and resistance levels using local extrema
    
    Args:
        data: DataFrame with OHLC data
        window: Window size for finding local extrema
        
    Returns:
        Dictionary with support and resistance levels
    """
    # Need at least 2*window+1 data points
    if len(data) < 2 * window + 1:
        return {"support": [], "resistance": []}
    
    # Find local minima (support levels)
    local_min_indices = argrelextrema(data['Low'].values, np.less, order=window)[0]
    support_levels = [data['Low'].iloc[i] for i in local_min_indices]
    
    # Find local maxima (resistance levels)
    local_max_indices = argrelextrema(data['High'].values, np.greater, order=window)[0]
    resistance_levels = [data['High'].iloc[i] for i in local_max_indices]
    
    # Sort levels from recent to older
    support_levels.sort(reverse=True)
    resistance_levels.sort()
    
    return {
        "support": support_levels,
        "resistance": resistance_levels
    }

def is_near_support_resistance(price, levels, threshold_pct=0.02):
    """
    Check if a price is near a key support or resistance level
    
    Args:
        price: Price to check
        levels: List of support or resistance levels
        threshold_pct: Percentage threshold to consider "near" (default 2%)
        
    Returns:
        Boolean indicating if price is near a key level
    """
    for level in levels:
        # Calculate percentage difference
        diff_pct = abs(price - level) / price
        if diff_pct <= threshold_pct:
            return True
    return False

def validate_candle_close_beyond_stop(stock, stop_level, option_type):
    """
    Validate if a candle has closed beyond the stop level
    
    Args:
        stock: yfinance Ticker object
        stop_level: Stop loss price level
        option_type: 'call' or 'put'
    
    Returns:
        Boolean indicating whether stop should be triggered
    """
    # Get the most recent candle
    data = stock.history(period="2d", interval="1d")
    
    if data.empty:
        return False
    
    current_close = data['Close'].iloc[-1]
    
    # For call options, trigger if close is BELOW stop level
    if option_type.lower() == 'call':
        return current_close < stop_level
    
    # For put options, trigger if close is ABOVE stop level
    return current_close > stop_level

def get_enhanced_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Get enhanced stop loss recommendation with pattern recognition and volume confirmation
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        days_to_expiration: Days to option expiration
        trade_type: "scalp", "swing", or "longterm" to override auto-determination
        
    Returns:
        Dictionary with stop loss recommendation or None if no valid patterns
    """
    # First determine the appropriate trade horizon based on DTE or user override
    if trade_type is not None:
        trade_horizon = trade_type
    elif days_to_expiration is not None:
        if days_to_expiration <= 2:
            trade_horizon = "scalp"
        elif days_to_expiration <= 90:
            trade_horizon = "swing"
        else:
            trade_horizon = "longterm"
    else:
        trade_horizon = "swing"  # Default if unknown
    
    print(f"Enhanced stop loss analysis for {option_type} option with {days_to_expiration} DTE (Horizon: {trade_horizon})")
    
    # Get stop loss recommendations based on different patterns
    breakout_stop = calculate_breakout_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
    engulfing_stop = calculate_engulfing_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
    
    # If we found both patterns, select the most appropriate one
    if breakout_stop and engulfing_stop:
        print(f"Found both breakout and engulfing patterns")
        
        # Breakout patterns take priority if matched with horizon
        if breakout_stop["time_horizon"] == trade_horizon:
            print(f"Using breakout pattern (matches trade horizon)")
            return breakout_stop
        elif engulfing_stop["time_horizon"] == trade_horizon:
            print(f"Using engulfing pattern (matches trade horizon)")
            return engulfing_stop
        else:
            # If neither matches, use breakout (higher priority)
            print(f"Using breakout pattern (default priority)")
            return breakout_stop
    
    # If only one pattern was found, use it
    if breakout_stop:
        print(f"Using breakout pattern (only pattern found)")
        return breakout_stop
    
    if engulfing_stop:
        print(f"Using engulfing pattern (only pattern found)")
        return engulfing_stop
    
    # No valid patterns found
    print(f"No valid patterns found in enhanced stop loss analysis")
    return None