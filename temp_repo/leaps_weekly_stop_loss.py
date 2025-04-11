"""
LEAPS Weekly-Based Stop Loss System

This module provides a simplified and reliable stop loss system for long-term options (LEAPS)
with 60+ DTE, using weekly candle structure with ATR-based buffering.

Key principles:
1. Uses weekly candle structure for macro analysis (ideal for LEAPS)
2. Applies 10% of weekly ATR as buffer (gives volatility tolerance)
3. Requires weekly candle close confirmation (filters out noise)
4. Ties to actual market behavior, not arbitrary percentages

Usage:
    from leaps_weekly_stop_loss import get_leaps_weekly_stop_loss
    
    # Get weekly-based LEAPS stop loss for options with 180 DTE
    stop_loss = get_leaps_weekly_stop_loss(stock, current_price, 'call', 180)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import datetime

def calculate_weekly_atr(data, window=14):
    """
    Calculate Average True Range (ATR) using weekly data
    
    Args:
        data: DataFrame with OHLC data (weekly)
        window: ATR period (default: 14)
        
    Returns:
        Latest ATR value
    """
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    
    atr = true_range.rolling(window).mean().iloc[-1]
    return atr

def calculate_leaps_weekly_stop_loss(entry_weekly_candle, atr_weekly, direction):
    """
    Stop-loss logic for LEAPS using weekly candle structure + ATR buffer.

    Parameters:
        entry_weekly_candle (dict): Weekly candle with 'high', 'low', 'close'.
        atr_weekly (float): ATR value based on weekly candles.
        direction (str): 'long' or 'short'.

    Returns:
        float: Stop-loss level to use.
    """
    buffer = 0.1 * atr_weekly  # 10% of ATR for LEAPS-level volatility

    if direction == 'long':
        stop_loss = entry_weekly_candle['low'] - buffer
    elif direction == 'short':
        stop_loss = entry_weekly_candle['high'] + buffer
    else:
        raise ValueError("Direction must be 'long' or 'short'")

    return round(stop_loss, 2)

def get_leaps_weekly_stop_loss(stock, current_price, option_type, days_to_expiration):
    """
    Get weekly-based LEAPS stop loss recommendation
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        days_to_expiration: Days to option expiration
    
    Returns:
        Dictionary with LEAPS stop loss recommendation or None if insufficient data
    """
    # Only proceed if this is a LEAPS trade (60+ DTE)
    if days_to_expiration < 60:
        print(f"Not a LEAPS trade ({days_to_expiration} DTE)")
        return None
    
    print(f"LEAPS weekly stop loss analysis for {option_type} option with {days_to_expiration} DTE")
    
    try:
        # Get weekly data (more appropriate for LEAPS)
        weekly_data = stock.history(period="6mo", interval="1wk")
        
        if weekly_data.empty or len(weekly_data) < 15:  # Need at least 15 weeks for reliable analysis
            print("Insufficient weekly data for LEAPS analysis")
            return None
        
        # Convert to dictionary format for the last complete weekly candle
        entry_weekly_candle = {
            'high': weekly_data['High'].iloc[-1],
            'low': weekly_data['Low'].iloc[-1],
            'close': weekly_data['Close'].iloc[-1],
            'open': weekly_data['Open'].iloc[-1],
        }
        
        # Calculate weekly ATR
        atr_weekly = calculate_weekly_atr(weekly_data)
        
        # Determine direction based on option type (call = long, put = short)
        direction = 'long' if option_type.lower() == 'call' else 'short'
        
        # Calculate stop loss level
        stop_level = calculate_leaps_weekly_stop_loss(entry_weekly_candle, atr_weekly, direction)
        
        # Calculate percentage change from current price for display
        if option_type.lower() == 'call':
            percentage = ((current_price - stop_level) / current_price) * 100
            direction_emoji = "📉"
        else:
            percentage = ((stop_level - current_price) / current_price) * 100
            direction_emoji = "📈"
        
        # Build recommendation
        recommendation = (
            f"{direction_emoji} **LEAPS STOP LOSS - WEEKLY CANDLE BASED** {direction_emoji}\n\n"
            f"• Stock Price Stop Level: ${stop_level:.2f} ({percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n"
            f"• Based on weekly candle {'low' if option_type.lower() == 'call' else 'high'} with 10% ATR buffer (${(0.1 * atr_weekly):.2f})\n"
            f"• Weekly ATR: ${atr_weekly:.2f}\n"
            f"• Weekly candle: High=${entry_weekly_candle['high']:.2f}, Low=${entry_weekly_candle['low']:.2f}, Close=${entry_weekly_candle['close']:.2f}\n"
            f"• Only exit if a weekly candle closes {'below' if option_type.lower() == 'call' else 'above'} ${stop_level:.2f}"
        )
        
        return {
            "level": stop_level,
            "recommendation": recommendation,
            "weekly_atr": atr_weekly,
            "atr_buffer": 0.1 * atr_weekly,
            "entry_candle": entry_weekly_candle,
            "time_horizon": "longterm"
        }
        
    except Exception as e:
        print(f"Error in LEAPS weekly stop loss calculation: {str(e)}")
        return None