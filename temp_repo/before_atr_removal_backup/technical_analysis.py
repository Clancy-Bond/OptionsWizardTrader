import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import datetime

# Import enhanced stop loss module
from enhanced_atr_stop_loss import (
    calculate_atr,
    get_volume_confirmation,
    identify_breakout_candle,
    identify_engulfing_candle,
    scale_atr_for_dte,
    calculate_breakout_stop_loss,
    calculate_engulfing_stop_loss,
    validate_candle_close_beyond_stop,
    get_enhanced_stop_loss
)

# Import combined scalp stop loss for 2DTE or less
from combined_scalp_stop_loss import get_combined_scalp_stop_loss



# Using calculate_atr from enhanced_atr_stop_loss.py module instead of defining it here

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
        # Not enough data to calculate
        return False, 0.0
    
    # Get the last volume and average of previous N periods
    current_volume = data['Volume'].iloc[-1]
    avg_volume = data['Volume'].iloc[-lookback-1:-1].mean()
    
    # Calculate ratio
    if avg_volume > 0:
        ratio = current_volume / avg_volume
        confirmation = ratio >= threshold
        return confirmation, ratio
    else:
        return False, 0.0

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
        
    # Get the recent data
    recent_data = data.iloc[-lookback-1:]
    latest_candle = recent_data.iloc[-1]
    prev_candles = recent_data.iloc[:-1]
    
    # Check for breakout by comparing latest candle to recent range
    prev_high = prev_candles['High'].max()
    prev_low = prev_candles['Low'].min()
    prev_close = prev_candles['Close'].iloc[-1]
    
    # Check volume
    volume_confirmed, volume_ratio = get_volume_confirmation(recent_data)
    
    # Check for CALL breakout (price breaks above previous range on strong volume)
    if latest_candle['Close'] > prev_high and volume_confirmed:
        return {
            "pattern": "breakout",
            "direction": "bullish",
            "entry_price": latest_candle['Close'],
            "stop_level": latest_candle['Low'],
            "volume_ratio": volume_ratio,
            "prev_high": prev_high,
            "prev_low": prev_low
        }
    
    # Check for PUT breakdown (price breaks below previous range on strong volume)
    elif latest_candle['Close'] < prev_low and volume_confirmed:
        return {
            "pattern": "breakdown",
            "direction": "bearish",
            "entry_price": latest_candle['Close'],
            "stop_level": latest_candle['High'],
            "volume_ratio": volume_ratio,
            "prev_high": prev_high,
            "prev_low": prev_low
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
        
    # Get the last two candles
    prev_candle = data.iloc[-2]
    current_candle = data.iloc[-1]
    
    # Check volume
    volume_confirmed, volume_ratio = get_volume_confirmation(data)
    
    # Bullish engulfing (for CALL options)
    if (prev_candle['Close'] < prev_candle['Open'] and  # Previous candle was bearish
        current_candle['Close'] > current_candle['Open'] and  # Current candle is bullish
        current_candle['Open'] <= prev_candle['Close'] and  # Current open below or equal to prev close
        current_candle['Close'] >= prev_candle['Open'] and  # Current close above or equal to prev open
        volume_confirmed):  # Volume confirmation
        
        return {
            "pattern": "engulfing",
            "direction": "bullish",
            "entry_price": current_candle['Close'],
            "stop_level": current_candle['Low'],
            "volume_ratio": volume_ratio
        }
    
    # Bearish engulfing (for PUT options)
    elif (prev_candle['Close'] > prev_candle['Open'] and  # Previous candle was bullish
        current_candle['Close'] < current_candle['Open'] and  # Current candle is bearish
        current_candle['Open'] >= prev_candle['Close'] and  # Current open above or equal to prev close
        current_candle['Close'] <= prev_candle['Open'] and  # Current close below or equal to prev open
        volume_confirmed):  # Volume confirmation
        
        return {
            "pattern": "engulfing",
            "direction": "bearish",
            "entry_price": current_candle['Close'],
            "stop_level": current_candle['High'],
            "volume_ratio": volume_ratio
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
    # If trade_type not specified, determine from DTE
    if trade_type is None:
        if days_to_expiration is None:
            trade_type = "swing"  # Default if unknown
        elif days_to_expiration <= 2:
            trade_type = "scalp"
        elif days_to_expiration <= 90:
            trade_type = "swing"
        else:
            trade_type = "longterm"
    
    # Base multiplier based on pattern type and trade type
    if pattern_type == "breakout":
        if trade_type == "scalp":
            base_multiplier = 0.08  # 0.08 × ATR for scalp breakout patterns
        elif trade_type == "longterm":
            base_multiplier = 0.12  # 0.12 × ATR for longterm breakout patterns
        else:  # swing
            base_multiplier = 0.10  # 0.10 × ATR for swing breakout patterns
    else:  # engulfing
        if trade_type == "scalp":
            base_multiplier = 0.04  # 0.04 × ATR for scalp engulfing patterns
        elif trade_type == "longterm":
            base_multiplier = 0.06  # 0.06 × ATR for longterm engulfing patterns
        else:  # swing
            base_multiplier = 0.05  # 0.05 × ATR for swing engulfing patterns
    
    # Adjust multiplier based on DTE
    if days_to_expiration is None:
        dte_multiplier = 1.0  # Default if DTE is unknown
    elif days_to_expiration < 7:
        dte_multiplier = 0.8  # Tighter stops for short-dated options
    elif days_to_expiration > 30:
        dte_multiplier = 1.2  # Wider stops for longer-dated options
    else:
        dte_multiplier = 1.0  # Standard for medium-term
    
    return atr * base_multiplier * dte_multiplier

def calculate_breakout_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss based on breakout/breakdown candle pattern with ATR buffer
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        days_to_expiration: Days to expiration
    
    Returns:
        Dictionary with stop loss recommendation based on breakout pattern
    """
    try:
        # Get relevant price data
        hist_data = stock.history(period="30d", interval="1d")
        
        if hist_data.empty:
            raise ValueError("Insufficient data available for analysis")
        
        # Calculate standard ATR
        atr = calculate_atr(hist_data, window=14, trade_type=trade_type)
        
        # Check for breakout/breakdown pattern
        pattern = identify_breakout_candle(hist_data)
        
        if pattern and pattern["direction"] == "bullish" and option_type.lower() == 'call':
            # Bullish breakout for CALL options
            entry_price = pattern["entry_price"]
            pattern_stop = pattern["stop_level"]
            
            # Calculate ATR buffer with DTE scaling
            atr_buffer = scale_atr_for_dte(atr, days_to_expiration or 14, "breakout", trade_type)
            
            # Final stop level below the pattern stop with ATR buffer
            stop_loss = pattern_stop - atr_buffer
            
            # Calculate percentage drop for display
            percentage_drop = ((current_price - stop_loss) / current_price) * 100
            
            # Recommendation with detailed pattern information
            return {
                "level": stop_loss,
                "pattern": "breakout",
                "entry": entry_price,
                "pattern_stop": pattern_stop,
                "atr_buffer": atr_buffer,
                "volume_ratio": pattern["volume_ratio"],
                "recommendation": f"📈 **BREAKOUT TRADE STOP LOSS** 📈\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Based on breakout candle low with {atr_buffer:.2f} ATR buffer\n• Volume confirmation: {pattern['volume_ratio']:.1f}x average volume",
                "time_horizon": "swing",
                "option_stop_price": None  # Will be calculated by calling function
            }
            
        elif pattern and pattern["direction"] == "bearish" and option_type.lower() == 'put':
            # Bearish breakdown for PUT options
            entry_price = pattern["entry_price"]
            pattern_stop = pattern["stop_level"]
            
            # Calculate ATR buffer with DTE scaling
            atr_buffer = scale_atr_for_dte(atr, days_to_expiration or 14, "breakout", trade_type)
            
            # Final stop level above the pattern stop with ATR buffer
            stop_loss = pattern_stop + atr_buffer
            
            # Calculate percentage rise for display
            percentage_rise = ((stop_loss - current_price) / current_price) * 100
            
            # Recommendation with detailed pattern information
            return {
                "level": stop_loss,
                "pattern": "breakdown",
                "entry": entry_price,
                "pattern_stop": pattern_stop,
                "atr_buffer": atr_buffer,
                "volume_ratio": pattern["volume_ratio"],
                "recommendation": f"📉 **BREAKDOWN TRADE STOP LOSS** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Based on breakdown candle high with {atr_buffer:.2f} ATR buffer\n• Volume confirmation: {pattern['volume_ratio']:.1f}x average volume",
                "time_horizon": "swing",
                "option_stop_price": None  # Will be calculated by calling function
            }
        
        # If no valid breakout pattern was found, return None
        return None
        
    except Exception as e:
        print(f"Error in breakout stop loss calculation: {str(e)}")
        return None

def calculate_engulfing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss based on engulfing candle pattern with ATR buffer
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        days_to_expiration: Days to expiration
    
    Returns:
        Dictionary with stop loss recommendation based on engulfing pattern
    """
    try:
        # Get relevant price data
        hist_data = stock.history(period="30d", interval="1d")
        
        if hist_data.empty:
            raise ValueError("Insufficient data available for analysis")
        
        # Calculate standard ATR
        atr = calculate_atr(hist_data, window=14, trade_type=trade_type)
        
        # Check for engulfing pattern
        pattern = identify_engulfing_candle(hist_data)
        
        if pattern and pattern["direction"] == "bullish" and option_type.lower() == 'call':
            # Bullish engulfing for CALL options
            entry_price = pattern["entry_price"]
            pattern_stop = pattern["stop_level"]
            
            # Calculate ATR buffer with DTE scaling
            atr_buffer = scale_atr_for_dte(atr, days_to_expiration or 14, "engulfing", trade_type)
            
            # Final stop level below the pattern stop with ATR buffer
            stop_loss = pattern_stop - atr_buffer
            
            # Calculate percentage drop for display
            percentage_drop = ((current_price - stop_loss) / current_price) * 100
            
            # Recommendation with detailed pattern information
            return {
                "level": stop_loss,
                "pattern": "engulfing",
                "entry": entry_price,
                "pattern_stop": pattern_stop,
                "atr_buffer": atr_buffer,
                "volume_ratio": pattern["volume_ratio"],
                "recommendation": f"📈 **ENGULFING CANDLE STOP LOSS** 📈\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Based on bullish engulfing candle low with {atr_buffer:.2f} ATR buffer\n• Volume confirmation: {pattern['volume_ratio']:.1f}x average volume",
                "time_horizon": "swing",
                "option_stop_price": None  # Will be calculated by calling function
            }
            
        elif pattern and pattern["direction"] == "bearish" and option_type.lower() == 'put':
            # Bearish engulfing for PUT options
            entry_price = pattern["entry_price"]
            pattern_stop = pattern["stop_level"]
            
            # Calculate ATR buffer with DTE scaling
            atr_buffer = scale_atr_for_dte(atr, days_to_expiration or 14, "engulfing", trade_type)
            
            # Final stop level above the pattern stop with ATR buffer
            stop_loss = pattern_stop + atr_buffer
            
            # Calculate percentage rise for display
            percentage_rise = ((stop_loss - current_price) / current_price) * 100
            
            # Recommendation with detailed pattern information
            return {
                "level": stop_loss,
                "pattern": "engulfing",
                "entry": entry_price,
                "pattern_stop": pattern_stop,
                "atr_buffer": atr_buffer,
                "volume_ratio": pattern["volume_ratio"],
                "recommendation": f"📉 **ENGULFING CANDLE STOP LOSS** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Based on bearish engulfing candle high with {atr_buffer:.2f} ATR buffer\n• Volume confirmation: {pattern['volume_ratio']:.1f}x average volume",
                "time_horizon": "swing",
                "option_stop_price": None  # Will be calculated by calling function
            }
        
        # If no valid engulfing pattern was found, return None
        return None
        
    except Exception as e:
        print(f"Error in engulfing stop loss calculation: {str(e)}")
        return None

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
    try:
        # Get most recent daily candle
        latest_data = stock.history(period="1d")
        
        if latest_data.empty:
            return False
            
        latest_close = latest_data['Close'].iloc[-1]
        
        # For CALL options, trigger if close is below stop
        if option_type.lower() == 'call':
            return latest_close < stop_level
        # For PUT options, trigger if close is above stop
        else:
            return latest_close > stop_level
            
    except Exception as e:
        print(f"Error validating candle close: {str(e)}")
        return False

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
    # Try breakout/breakdown pattern first
    breakout_stop = calculate_breakout_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type)
    
    # If breakout pattern found, return it
    if breakout_stop:
        return breakout_stop
        
    # Otherwise try engulfing pattern
    engulfing_stop = calculate_engulfing_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type)
    
    # If engulfing pattern found, return it
    if engulfing_stop:
        return engulfing_stop
        
    # If no patterns found, return None
    return None
# Using imported calculate_atr from enhanced_atr_stop_loss.py

def get_support_levels(stock, periods=[14, 30, 90]):
    """
    Calculate support levels using historical price data.
    
    Args:
        stock: yfinance Ticker object
        periods: List of time periods to analyze
    
    Returns:
        List of support levels
    """
    try:
        # Get historical data for different time periods
        support_levels = []
        
        for period in periods:
            # Get historical data
            hist = stock.history(period=f"{period}d")
            
            if hist.empty:
                continue
                
            # Find local minima (support levels)
            order = min(5, len(hist) // 10)  # Adaptive order based on data length
            if order > 0:
                local_min_indices = argrelextrema(hist['Low'].values, np.less, order=order)[0]
                support_prices = hist['Low'].iloc[local_min_indices].values
                
                # Add to support levels
                support_levels.extend(support_prices)
        
        # Get current price
        current_price = stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
        
        # Filter support levels that are below current price
        valid_supports = [level for level in support_levels if level < current_price]
        
        # If no valid supports, we need to look at a longer time frame to find technical levels
        if not valid_supports:
            # Try looking at a longer time period
            longer_hist = stock.history(period="6mo")
            if not longer_hist.empty:
                order = min(5, len(longer_hist) // 10)
                if order > 0:
                    local_min_indices = argrelextrema(longer_hist['Low'].values, np.less, order=order)[0]
                    additional_support_prices = longer_hist['Low'].iloc[local_min_indices].values
                    valid_supports.extend([level for level in additional_support_prices if level < current_price])
                    
            # If still no valid supports, which should be rare, sort and filter what we have
            if not valid_supports:
                print("Warning: No technical support levels found. Please review manually.")
        
        # Sort and remove duplicates
        valid_supports = sorted(list(set([round(level, 2) for level in valid_supports])), reverse=True)
        
        return valid_supports
    except Exception as e:
        print(f"Error calculating support levels: {str(e)}")
        # Try to get historical data to find technical levels
        try:
            # Use a more straightforward approach to find support levels
            hist_data = stock.history(period="6mo")
            if not hist_data.empty:
                # Find the lowest points in recent history
                hist_data['Lower'] = hist_data['Low'].rolling(window=5).min()
                
                # Sort the data by the 'Lower' values (lowest first)
                lower_levels = sorted(hist_data['Lower'].dropna().unique())
                
                # Filter to levels below the current price
                current_price = stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
                valid_supports = [level for level in lower_levels if level < current_price]
                
                if valid_supports:
                    # Return the 3 highest support levels below current price
                    return [round(level, 2) for level in reversed(valid_supports[:3])]
        except:
            pass
            
        # Only if all else fails, fall back to this approach
        print("Using last-resort method for support levels")
        current_price = stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
        
        # Try to get some recent volatility data to make the levels more relevant
        try:
            hist_data = stock.history(period="30d")
            if not hist_data.empty:
                # Calculate typical daily range as a percentage
                typical_range = (hist_data['High'] - hist_data['Low']).mean() / current_price
                level1 = current_price * (1 - typical_range * 2)  # 2x typical daily range
                level2 = current_price * (1 - typical_range * 3)  # 3x typical daily range
                level3 = current_price * (1 - typical_range * 4)  # 4x typical daily range
                return [round(level1, 2), round(level2, 2), round(level3, 2)]
        except:
            pass
        
        # Absolute last resort
        return [
            round(current_price * 0.95, 2),
            round(current_price * 0.90, 2),
            round(current_price * 0.85, 2)
        ]

def get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss recommendations for scalp/day trades.
    For options with 2DTE or less, uses a combined VWAP and wick-based approach.
    For 3+ DTE, falls back to the standard approach.
    
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
        # Check if this is 2DTE or less - if so, use our combined approach
        if days_to_expiration is not None and days_to_expiration <= 2:
            # Use combined VWAP and wick-based approach for 2DTE or less
            return get_combined_scalp_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type)
        
        # If more than 2DTE, use the standard approach below
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
        
        # Calculate ATR for volatility-based stop
        atr = calculate_atr(hist_data, window=7, trade_type=trade_type)  # Use 7-period ATR for scalp trades
        
        # For scalp trades, we'll use a much tighter stop based on ATR
        if option_type.lower() == 'call':
            # For long trades in call options
            
            # Set the buffer based on ATR but with DTE considerations
            # Use smaller percentage for 0-1 DTE
            if days_to_expiration is not None and days_to_expiration <= 3:
                buffer_percentage = 0.97  # 3% max drop for 3 DTE
                atr_multiple = 1.2
            else:
                buffer_percentage = 0.95  # 5% max drop for other scalps
                atr_multiple = 1.5
            
            # Calculate stop loss directly from recent price action
            recent_low = hist_data['Low'].iloc[-5:].min()
            
            # Add a buffer based on ATR
            atr_buffer = atr * atr_multiple
            
            # Use the higher of the two (more conservative)
            stop_loss = max(recent_low - atr_buffer, current_price * buffer_percentage)
            
            # Calculate percentage drop
            percentage_drop = ((current_price - stop_loss) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS ({timeframe}-chart)** ⚡\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Based on recent price action with {atr_multiple:.1f}x ATR buffer",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }
        else:
            # For put options (short bias)
            
            # Set the buffer based on ATR but with DTE considerations
            if days_to_expiration is not None and days_to_expiration <= 3:
                buffer_percentage = 1.03  # 3% max rise for 3 DTE
                atr_multiple = 1.2
            else:
                buffer_percentage = 1.05  # 5% max rise for other scalps
                atr_multiple = 1.5
            
            # Calculate stop loss directly from recent price action
            recent_high = hist_data['High'].iloc[-5:].max()
            
            # Add a buffer based on ATR
            atr_buffer = atr * atr_multiple
            
            # Use the lower of the two (more conservative)
            stop_loss = min(recent_high + atr_buffer, current_price * buffer_percentage)
            
            # Calculate percentage rise
            percentage_rise = ((stop_loss - current_price) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS ({timeframe}-chart)** ⚡\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Based on recent price action with {atr_multiple:.1f}x ATR buffer",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }
            
    except Exception as e:
        print(f"Error calculating scalp stop loss: {str(e)}")
        # Fallback to simple percentage based on option type
        if option_type.lower() == 'call':
            stop_loss = current_price * 0.98  # 2% drop for scalp
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min)** ⚡\n\n• Stock Price Stop Level: ${stop_loss:.2f} (2% below current price)\n• Standard scalp-trade protection level",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }
        else:
            # Adjust fallback based on days to expiration
            max_percentage = 1.02  # Default 2% buffer for scalp
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 1:
                    max_percentage = 1.01  # 1% for 0-1 DTE
            
            stop_loss = current_price * max_percentage  # Dynamic percentage for scalp
            # Calculate percentage change for display
            percentage_change = (max_percentage - 1.0) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15 min chart)** ⚡\n\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_change:.1f}% above current price)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }

def get_swing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss recommendations for swing trades (4h-charts)
    Suitable for options with 2 weeks to 3 months expiry
    
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
        # Get 4-hour data for swing trades (approximately 7 trading days = 35-40 4h candles)
        hist_data = stock.history(period="7d", interval="4h")
        
        # Fall back to daily data if 4h is not available (common for some stocks)
        if hist_data.empty:
            hist_data = stock.history(period="30d", interval="1d")
            if hist_data.empty:
                raise ValueError("Insufficient data available")
        
        # Calculate ATR for volatility-based stop
        atr = calculate_atr(hist_data, window=14, trade_type=trade_type)  # Standard 14-period ATR
        
        # Look for engulfing/reversal candle patterns
        if option_type.lower() == 'call':
            # For long trades in call options
            
            # For swing trades on calls, we'll use key support levels
            # Find a recent support level with validation
            support_levels = get_support_levels(stock, periods=[14, 30])
            
            valid_supports = [level for level in support_levels if level < current_price]
            
            if valid_supports:
                # Use the highest support level below current price
                support_level = valid_supports[0]
                
                # Add a buffer based on ATR (less tight than scalp, but still respects recent price action)
                # Calculate dynamic buffer based on days to expiration
                min_percentage = 0.95  # Default 5% max buffer
                buffer_factor = 0.5    # Default ATR factor
                
                # Adjust buffer based on days to expiration if available
                if days_to_expiration is not None:
                    if days_to_expiration <= 1:
                        min_percentage = 0.99  # 1% for 0-1 DTE
                        buffer_factor = 0.2    # Smaller ATR multiple
                    elif days_to_expiration <= 2:
                        min_percentage = 0.98  # 2% for 2 DTE
                        buffer_factor = 0.3    # Smaller ATR multiple
                    elif days_to_expiration <= 5:
                        min_percentage = 0.97  # 3% for 3-5 DTE
                        buffer_factor = 0.4    # Smaller ATR multiple
                
                
                # Calculate the buffer to add to the support level
                technical_buffer = buffer_factor * atr
                
                # Calculate the stop loss using the technical support level with buffer
                technical_stop = support_level - technical_buffer
                
                # Calculate what the minimum allowed stop loss would be (max buffer)
                min_allowed_stop = current_price * min_percentage
                
                # Calculate the percentage drops for both approaches
                technical_percentage = ((current_price - technical_stop) / current_price) * 100
                buffer_percentage = ((current_price - min_allowed_stop) / current_price) * 100
                
                # Determine which strategy to use based on which one is more conservative
                if technical_stop < min_allowed_stop:
                    # Technical stop exceeds maximum buffer percentage, so cap it
                    stop_loss = min_allowed_stop
                    stop_basis = "maximum buffer limit"
                    percentage_drop = buffer_percentage
                else:
                    # Technical stop is valid (within buffer limits), so use it
                    stop_loss = technical_stop
                    stop_basis = "key technical support"
                    percentage_drop = technical_percentage
                
                # Log what we're doing
                print(f"Technical stop: ${technical_stop:.2f} ({technical_percentage:.2f}%), Buffer limit: ${min_allowed_stop:.2f} ({buffer_percentage:.2f}%)")
                print(f"Using {stop_basis} for stop loss at ${stop_loss:.2f}")
                
                # Calculate percentage drop
                percentage_drop = ((current_price - stop_loss) / current_price) * 100
                
                return {
                    "level": stop_loss,
                    "recommendation": f"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Based on {stop_basis} zone with volatility analysis",
                    "time_horizon": "swing",
                    "option_stop_price": current_price * 0.5  # Simplified estimation
                }
            else:
                # If no clear support found, use ATR-based method
                # Calculate dynamic buffer based on days to expiration
                atr_multiple = 2.0  # Default 2x ATR
                min_percentage = 0.95  # Default 5% cap
                
                # Adjust buffer based on days to expiration if available
                if days_to_expiration is not None:
                    if days_to_expiration <= 1:
                        atr_multiple = 1.0  # 1x ATR for 0-1 DTE
                        min_percentage = 0.99  # 1% cap
                    elif days_to_expiration <= 2:
                        atr_multiple = 1.2  # 1.2x ATR for 2 DTE
                        min_percentage = 0.98  # 2% cap
                    elif days_to_expiration <= 5:
                        atr_multiple = 1.5  # 1.5 ATR for 3-5 DTE
                        min_percentage = 0.97  # 3% cap
                
                # Calculate both stop loss approaches
                stop_loss_atr = current_price - (atr_multiple * atr)
                stop_loss_buffer = current_price * min_percentage
                
                # Calculate percentages for both
                atr_percentage = ((current_price - stop_loss_atr) / current_price) * 100
                buffer_percentage = ((current_price - stop_loss_buffer) / current_price) * 100
                
                # Determine which to use
                if stop_loss_atr < stop_loss_buffer:
                    # ATR-based stop exceeds maximum buffer, so cap it
                    stop_loss = stop_loss_buffer
                    stop_basis = f"buffer limit ({buffer_percentage:.1f}%)"
                    percentage_drop = buffer_percentage
                else:
                    # ATR-based stop is within limits, so use it
                    stop_loss = stop_loss_atr
                    stop_basis = f"{atr_multiple}x ATR"
                    percentage_drop = atr_percentage
                
                # Log what we're doing
                print(f"ATR stop: ${stop_loss_atr:.2f} ({atr_percentage:.2f}%), Buffer limit: ${stop_loss_buffer:.2f} ({buffer_percentage:.2f}%)")
                print(f"Using {stop_basis} for stop loss at ${stop_loss:.2f}")
                percentage_drop = ((current_price - stop_loss) / current_price) * 100
                
                return {
                    "level": stop_loss,
                    "recommendation": f"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Based on {stop_basis}",
                    "time_horizon": "swing",
                    "option_stop_price": current_price * 0.5
                }
        else:
            # For put options (short bias)
            
            # Try to find recent resistance levels
            try:
                # Get historical data for different time periods
                resistance_levels = []
                for period in [14, 30]:
                    hist = stock.history(period=f"{period}d")
                    if not hist.empty:
                        order = min(5, len(hist) // 10)
                        if order > 0:
                            local_max_indices = argrelextrema(hist['High'].values, np.greater, order=order)[0]
                            resistance_prices = hist['High'].iloc[local_max_indices].values
                            resistance_levels.extend(resistance_prices)
                
                # Filter resistance levels that are above current price
                valid_resistances = [level for level in resistance_levels if level > current_price]
                
                if valid_resistances:
                    # Sort and get the closest resistance above current price
                    valid_resistances = sorted(valid_resistances)
                    resistance_level = valid_resistances[0]
                    
                    # Add buffer based on ATR
                    # Calculate dynamic buffer based on days to expiration
                    max_percentage = 1.05  # Default 5% max buffer
                    buffer_factor = 0.5    # Default ATR factor
                    
                    # Adjust buffer based on days to expiration if available
                    if days_to_expiration is not None:
                        if days_to_expiration <= 1:
                            max_percentage = 1.01  # 1% for 0-1 DTE
                            buffer_factor = 0.2    # Smaller ATR multiple
                        elif days_to_expiration <= 2:
                            max_percentage = 1.02  # 2% for 2 DTE
                            buffer_factor = 0.3    # Smaller ATR multiple
                        elif days_to_expiration <= 5:
                            max_percentage = 1.03  # 3% for 3-5 DTE
                            buffer_factor = 0.4    # Smaller ATR multiple
                    
                    
                    # Calculate the buffer to add to the resistance level
                    technical_buffer = buffer_factor * atr
                    
                    # Calculate the stop loss using the technical resistance level with buffer
                    technical_stop = resistance_level + technical_buffer
                    
                    # Calculate what the maximum allowed stop loss would be (max buffer)
                    max_allowed_stop = current_price * max_percentage
                    
                    # Calculate the percentage rises for both approaches
                    technical_percentage = ((technical_stop - current_price) / current_price) * 100
                    buffer_percentage = ((max_allowed_stop - current_price) / current_price) * 100
                    
                    # Determine which strategy to use based on which one is more conservative
                    if technical_stop > max_allowed_stop:
                        # Technical stop exceeds maximum buffer percentage, so cap it
                        stop_loss = max_allowed_stop
                        stop_basis = "maximum buffer limit"
                        percentage_rise = buffer_percentage
                    else:
                        # Technical stop is valid (within buffer limits), so use it
                        stop_loss = technical_stop
                        stop_basis = "key technical resistance"
                        percentage_rise = technical_percentage
                    
                    # Log what we're doing
                    print(f"Technical stop: ${technical_stop:.2f} ({technical_percentage:.2f}%), Buffer limit: ${max_allowed_stop:.2f} ({buffer_percentage:.2f}%)")
                    print(f"Using {stop_basis} for stop loss at ${stop_loss:.2f}")
                    
                    # Calculate percentage rise
                    percentage_rise = ((stop_loss - current_price) / current_price) * 100
                    
                    return {
                        "level": stop_loss,
                        "recommendation": f"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Based on {stop_basis} zone with volatility analysis",
                        "time_horizon": "swing",
                        "option_stop_price": current_price * 0.5
                    }
                else:
                    # If no clear resistance found, use ATR-based method
                    # Calculate dynamic buffer based on days to expiration
                    atr_multiple = 2.0  # Default 2x ATR
                    max_percentage = 1.05  # Default 5% cap
                
                    # Adjust buffer based on days to expiration if available
                    if days_to_expiration is not None:
                        if days_to_expiration <= 1:
                            atr_multiple = 1.0  # 1x ATR for 0-1 DTE
                            max_percentage = 1.01  # 1% cap
                        elif days_to_expiration <= 2:
                            atr_multiple = 1.2  # 1.2x ATR for 2 DTE
                            max_percentage = 1.02  # 2% cap
                        elif days_to_expiration <= 5:
                            atr_multiple = 1.5  # 1.5 ATR for 3-5 DTE
                            max_percentage = 1.03  # 3% cap
                    
                    # Calculate both stop loss approaches
                    stop_loss_atr = current_price + (atr_multiple * atr)
                    stop_loss_buffer = current_price * max_percentage
                    
                    # Calculate percentages for both
                    atr_percentage = ((stop_loss_atr - current_price) / current_price) * 100
                    buffer_percentage = ((stop_loss_buffer - current_price) / current_price) * 100
                    
                    # Determine which to use
                    if stop_loss_atr > stop_loss_buffer:
                        # ATR-based stop exceeds maximum buffer, so cap it
                        stop_loss = stop_loss_buffer
                        stop_basis = f"buffer limit ({buffer_percentage:.1f}%)"
                        percentage_rise = buffer_percentage
                    else:
                        # ATR-based stop is within limits, so use it
                        stop_loss = stop_loss_atr
                        stop_basis = f"{atr_multiple}x ATR"
                        percentage_rise = atr_percentage
                    
                    # Log what we're doing
                    print(f"ATR stop: ${stop_loss_atr:.2f} ({atr_percentage:.2f}%), Buffer limit: ${stop_loss_buffer:.2f} ({buffer_percentage:.2f}%)")
                    print(f"Using {stop_basis} for stop loss at ${stop_loss:.2f}")
                    percentage_rise = ((stop_loss - current_price) / current_price) * 100
                    
                    return {
                        "level": stop_loss,
                        "recommendation": f"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Based on {stop_basis}",
                        "time_horizon": "swing",
                        "option_stop_price": current_price * 0.5
                    }
            except Exception as e:
                print(f"Error in swing trade resistance calculation: {str(e)}")
                # Fallback
                # Adjust fallback based on days to expiration
                max_percentage = 1.04  # Default 4% buffer
                
                # Adjust buffer based on days to expiration if available
                if days_to_expiration is not None:
                    if days_to_expiration <= 1:
                        max_percentage = 1.01  # 1% for 0-1 DTE
                    elif days_to_expiration <= 2:
                        max_percentage = 1.02  # 2% for 2 DTE
                    elif days_to_expiration <= 5:
                        max_percentage = 1.03  # 3% for 3-5 DTE
                
                stop_loss = current_price * max_percentage  # Dynamic percentage for swing
                # Calculate percentage change for display
                percentage_change = (max_percentage - 1.0) * 100
                
                return {
                    "level": stop_loss,
                    "recommendation": f"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_change:.1f}% above current price)\n• Conservative protection level",
                    "time_horizon": "swing",
                    "option_stop_price": current_price * 0.5
                }
                
    except Exception as e:
        print(f"Error calculating swing stop loss: {str(e)}")
        # Fallback to simple percentage based on option type
        if option_type.lower() == 'call':
            stop_loss = current_price * 0.93  # 7% drop for swing
            return {
                "level": stop_loss,
                "recommendation": f"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\n\n• Stock Price Stop Level: ${stop_loss:.2f} (7% below current price)\n• Standard swing-trade protection level",
                "time_horizon": "swing",
                "option_stop_price": current_price * 0.5
            }
        else:
            stop_loss = current_price * 1.07  # 7% rise for swing
            return {
                "level": stop_loss,
                "recommendation": f"📉 **SWING TRADE STOP LOSS (4H/Daily chart)** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} (7% above current price)\n• Standard swing-trade protection level",
                "time_horizon": "swing",
                "option_stop_price": current_price * 0.5
            }

def get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss recommendations for long-term trades (weekly charts)
    Suitable for options with 6+ months expiry
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
    
    Returns:
        Dictionary with stop loss recommendation
    """
    try:
        # Get weekly data for the past 6 months
        hist_data = stock.history(period="6mo", interval="1wk")
        
        if hist_data.empty:
            raise ValueError("Insufficient weekly data available")
        
        # Calculate ATR for volatility-based stop
        atr = calculate_atr(hist_data, window=10, trade_type=trade_type)  # 10-week ATR for long-term
        
        # For long-term trades, we want to respect major technical levels
        if option_type.lower() == 'call':
            # Find significant support zones (weekly lows)
            # We'll use a mix of key support levels and trend analysis
            
            # Calculate a wider dynamic range based on the ATR over a longer period
            # For elite positions (LEAPS, etc), we need a wider stop to avoid early exit
            atr_multiple = 2.5  # Default 2.5x ATR
            max_drop_percentage = 0.12  # Default 12% maximum drop for long-term
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 5:
                    atr_multiple = 1.5  # 1.5x ATR for shorter expirations
                    max_drop_percentage = 0.05  # 5% for shorter expirations
                elif days_to_expiration <= 14:
                    atr_multiple = 1.8  # 1.8x ATR for medium-term
                    max_drop_percentage = 0.08  # 8% for medium-term
                elif days_to_expiration <= 30:
                    atr_multiple = 2.0  # 2.0x ATR for longer-term
                    max_drop_percentage = 0.10  # 10% for longer-term
                    
            stop_loss = current_price - (atr_multiple * atr)
            
            # Ensure it's not too tight
            floor_level = current_price * (1 - max_drop_percentage)
            
            stop_loss = max(stop_loss, floor_level)
            
            # Calculate percentage drop
            percentage_drop = ((current_price - stop_loss) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Based on weekly ATR (volatility) with wider buffer",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5  # Simplified estimation
            }
        else:
            # For put options (short bias) with long-term outlook
            
            # Calculate a wider dynamic range based on ATR
            atr_multiple = 2.5  # Default 2.5x ATR
            max_rise_percentage = 0.12  # Default 12% maximum rise for long-term
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 5:
                    atr_multiple = 1.5  # 1.5x ATR for shorter expirations
                    max_rise_percentage = 0.05  # 5% for shorter expirations
                elif days_to_expiration <= 14:
                    atr_multiple = 1.8  # 1.8x ATR for medium-term
                    max_rise_percentage = 0.08  # 8% for medium-term
                elif days_to_expiration <= 30:
                    atr_multiple = 2.0  # 2.0x ATR for longer-term
                    max_rise_percentage = 0.10  # 10% for longer-term
                    
            stop_loss = current_price + (atr_multiple * atr)
            
            # Ensure it's not too tight
            ceiling_level = current_price * (1 + max_rise_percentage)
            
            stop_loss = min(stop_loss, ceiling_level)
            
            # Calculate percentage rise
            percentage_rise = ((stop_loss - current_price) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Based on weekly ATR (volatility) with wider buffer",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5
            }
                
    except Exception as e:
        print(f"Error calculating long-term stop loss: {str(e)}")
        # Fallback to simple percentage based on option type
        if option_type.lower() == 'call':
            # Adjust fallback based on days to expiration
            min_percentage = 0.85  # Default 15% drop for long-term
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 5:
                    min_percentage = 0.95  # 5% for shorter expirations
                elif days_to_expiration <= 14:
                    min_percentage = 0.92  # 8% for medium-term
                elif days_to_expiration <= 30:
                    min_percentage = 0.90  # 10% for longer-term
                    
            stop_loss = current_price * min_percentage
            # Calculate percentage drop for display
            percentage_drop = ((current_price - stop_loss) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Conservative long-term protection level",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5
            }
        else:
            # Adjust fallback based on days to expiration
            max_percentage = 1.15  # Default 15% rise for long-term
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 5:
                    max_percentage = 1.05  # 5% for shorter expirations
                elif days_to_expiration <= 14:
                    max_percentage = 1.08  # 8% for medium-term
                elif days_to_expiration <= 30:
                    max_percentage = 1.10  # 10% for longer-term
                    
            stop_loss = current_price * max_percentage
            # Calculate percentage rise for display
            percentage_rise = ((stop_loss - current_price) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Conservative long-term protection level",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5
            }

def get_stop_loss_recommendation(stock, current_price, option_type, expiration=None):
    """
    Get comprehensive stop loss recommendations based on expiration timeframe.
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        expiration: Option expiration date (string in format 'YYYY-MM-DD')
    
    Returns:
        Dictionary with stop loss recommendations for different timeframes
    """
    try:
        # Determine the appropriate timeframe based on expiration if provided
        trade_horizon = "unknown"
        days_to_expiration = None
        
        if expiration:
            # Calculate days to expiration
            try:
                expiry_date = datetime.datetime.strptime(expiration, '%Y-%m-%d').date()
                today = datetime.datetime.now().date()
                days_to_expiration = (expiry_date - today).days
                
                if days_to_expiration <= 2:
                    trade_horizon = "scalp"  # Today or tomorrow expiry
                elif days_to_expiration <= 90:
                    trade_horizon = "swing"  # 2 weeks to 3 months
                else:
                    trade_horizon = "longterm"  # 6+ months
                    
                print(f"Days to expiration: {days_to_expiration}, Trade horizon: {trade_horizon}")
            except Exception as e:
                print(f"Error parsing expiration date: {str(e)}")
                # If date parsing fails, provide all recommendations
                trade_horizon = "unknown"
        
        # First, try to get pattern-based stop loss using the enhanced system
        enhanced_stop = get_enhanced_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
        
        # Get standard recommendations 
        scalp_recommendation = get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
        swing_recommendation = get_swing_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
        longterm_recommendation = get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
        
        # Create a result dictionary to store all recommendations
        result = {
            "scalp": scalp_recommendation,
            "swing": swing_recommendation,
            "longterm": longterm_recommendation,
            "trade_horizon": trade_horizon
        }
        
        # If enhanced stop loss was found, add it to the result and prioritize it
        if enhanced_stop:
            result["enhanced"] = enhanced_stop
            
            # If the enhanced stop is of pattern type, use it as primary
            # when it aligns with the trade horizon (or trade horizon is unknown)
            if trade_horizon == "unknown" or enhanced_stop["time_horizon"] == trade_horizon:
                result["primary"] = enhanced_stop
                # Add note about pattern-based stop loss
                print(f"Using pattern-based stop loss: {enhanced_stop['pattern']} pattern")
        
        # Set the primary recommendation based on the trade horizon
        # Only set if not already set by enhanced stop loss
        # Set the primary recommendation based on the trade horizon        # Only set if not already set by enhanced stop loss        if "primary" not in result:            if trade_horizon == "scalp":                try:                    result["primary"] = scalp_recommendation                                        # Create a completely integrated stop loss message                    base_msg = result["primary"]["recommendation"].replace(                        "Technical stop loss:", "Technical stock price stop:"                    )                                        # Get just the first section (the header and bullet points)                    base_parts = base_msg.split("\n\n")                    if len(base_parts) > 0:                        first_section = base_parts[0]                                                # Build a completely new message with proper sections                        result["primary"]["recommendation"] = (                            f"{first_section}\n"                            f"• For short-term options (1-2 days expiry)\n\n"                        )                                                # Add the appropriate warning based on option type                        if option_type.lower() == 'call' and result["primary"]["level"] < current_price:                            result["primary"]["recommendation"] += (                                f"⚠️ Options typically lose 70-90% of value when the stock hits stop level due to accelerated delta decay and negative gamma."                            )                        elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:                            result["primary"]["recommendation"] += (                                f"⚠️ Options typically lose 70-90% of value when the stock hits stop level due to accelerated delta decay and negative gamma."                            )                except Exception as e:                    print(f"Error formatting scalp recommendation: {e}")                        elif trade_horizon == "swing":                try:                    result["primary"] = swing_recommendation                                        # Create a completely integrated stop loss message                    base_msg = result["primary"]["recommendation"].replace(                        "Technical stop loss:", "Technical stock price stop:"                    )                                        # Get just the first section (the header and bullet points)                    base_parts = base_msg.split("\n\n")                    if len(base_parts) > 0:                        first_section = base_parts[0]                                                # Build a completely new message with proper sections                        result["primary"]["recommendation"] = (                            f"{first_section}\n"                            f"• For medium-term options (up to 90 days expiry)\n\n"                        )                                                # Add the appropriate warning based on option type                        if option_type.lower() == 'call' and result["primary"]["level"] < current_price:                            result["primary"]["recommendation"] += (                                f"⚠️ Options typically lose 60-80% of value when the stock hits stop level due to accelerated delta decay and negative gamma."                            )                        elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:                            result["primary"]["recommendation"] += (                                f"⚠️ Options typically lose 60-80% of value when the stock hits stop level due to accelerated delta decay and negative gamma."                            )                except Exception as e:                    print(f"Error formatting swing recommendation: {e}")                        elif trade_horizon == "longterm":                try:                    result["primary"] = longterm_recommendation                                        # Create a completely integrated stop loss message                    base_msg = result["primary"]["recommendation"].replace(                        "Technical stop loss:", "Technical stock price stop:"                    )                                        # Get just the first section (the header and bullet points)                    base_parts = base_msg.split("\n\n")                    if len(base_parts) > 0:                        first_section = base_parts[0]                                                # Build a completely new message with proper sections                        result["primary"]["recommendation"] = (                            f"{first_section}\n"                            f"• For long-term options (6+ months expiry)\n\n"                        )                                                # Add the appropriate warning based on option type                        if option_type.lower() == 'call' and result["primary"]["level"] < current_price:                            result["primary"]["recommendation"] += (                                f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."                            )                        elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:                            result["primary"]["recommendation"] += (                                f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."                            )                except Exception as e:                    print(f"Error formatting longterm recommendation: {e}")                        else:  # unknown trade horizon                # Set a default primary recommendation (use swing as default)                result["primary"] = {                    "level": swing_recommendation["level"],  # Default to swing as primary                    "recommendation": "Based on your option details, here are stop-loss recommendations for different trading timeframes. Choose the one that matches your trading strategy and option expiration:\n\n" +                                     "1. " + scalp_recommendation["recommendation"] + "\n\n" +                                    "2. " + swing_recommendation["recommendation"] + "\n\n" +                                    "3. " + longterm_recommendation["recommendation"] + "\n\n" +                                    "For more precise option price stop-loss calculations, please provide your specific option expiration date.",                    "time_horizon": "multiple"                }        # If we have the expiration date, only include recommendations appropriate for the timeframe
        if days_to_expiration is not None:
            # Filter recommendations based on expiration date
            # First check if we have a primary key in the result
            filtered_result = {"trade_horizon": trade_horizon}
            
            # Only add the primary key from result if it exists, otherwise use swing as default
            if "primary" in result:
                filtered_result["primary"] = result["primary"]
            elif "swing" in result:
                filtered_result["primary"] = result["swing"]
                print("Using swing recommendation as primary (fallback)")
            
            # Include only relevant timeframe recommendations
            if days_to_expiration <= 2:
                filtered_result["scalp"] = result["scalp"]
            
            if days_to_expiration > 2 and days_to_expiration <= 90:
                filtered_result["swing"] = result["swing"]
            
            if days_to_expiration > 90:
                filtered_result["longterm"] = result["longterm"]
            
            # Ensure all necessary keys exist in filtered_result
            if 'primary' not in filtered_result:
                filtered_result['primary'] = filtered_result.get('swing', result.get('swing'))
                
            # Always ensure trade_horizon is in the filtered_result
            filtered_result['trade_horizon'] = trade_horizon
            
            # Final safety check - if there's still no primary key, we need to ensure it exists
            if 'primary' not in filtered_result:
                # Look for any recommendation we can use as primary
                if 'scalp' in filtered_result:
                    filtered_result['primary'] = filtered_result['scalp']
                    print("Using scalp recommendation as primary (final fallback)")
                elif 'swing' in filtered_result:
                    filtered_result['primary'] = filtered_result['swing']
                    print("Using swing recommendation as primary (final fallback)")
                elif 'longterm' in filtered_result:
                    filtered_result['primary'] = filtered_result['longterm']
                    print("Using longterm recommendation as primary (final fallback)")
                else:
                    # Create a very basic primary recommendation as absolute last resort
                    filtered_result['primary'] = {
                        "level": current_price * 0.95 if option_type.lower() == 'call' else current_price * 1.05,
                        "recommendation": f"📊 **Stock Price Stop Level: ${current_price * 0.95 if option_type.lower() == 'call' else current_price * 1.05:.2f}** 📊",
                        "time_horizon": trade_horizon
                    }
                    print("Created emergency fallback recommendation as primary")
            
            print(f"Final filtered_result keys: {filtered_result.keys()}")
            return filtered_result
        
        # Ensure all necessary keys exist to prevent KeyError
        if 'primary' not in result:
            # Default to swing recommendation as primary if not already set
            result['primary'] = result['swing']
            
        # Always ensure trade_horizon is in the result
        result['trade_horizon'] = trade_horizon
        
        # Ensure all necessary keys exist to prevent KeyError
        if 'primary' not in result:
            # Default to swing recommendation as primary if not already set
            result['primary'] = result['swing']
            
        # Always ensure trade_horizon is in the result
        result['trade_horizon'] = trade_horizon
        
        return result    
    except Exception as e:
        print(f"Error in comprehensive stop loss calculation: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Fall back to the original implementation if errors occur
        # Get support levels
        support_levels = get_support_levels(stock)
        
        # For call options, we recommend stopping out if the price falls below a support level
        if option_type.lower() == 'call':
            # Get the closest support level below current price
            closest_support = None
            for level in support_levels:
                if level < current_price:
                    closest_support = level
                    break
            
            if closest_support is None:
                # If we still don't have a support level, use historical lows
                try:
                    # Get 6-month low as a last resort technical level
                    hist_6mo = stock.history(period="6mo")
                    if not hist_6mo.empty:
                        closest_support = hist_6mo['Low'].min() * 1.02  # Slightly above the absolute low
                    else:
                        # Really shouldn't happen, but as a last resort:
                        closest_support = current_price * 0.95
                except:
                    closest_support = current_price * 0.95
            
            # Calculate the percentage drop to the support level
            percentage_drop = ((current_price - closest_support) / current_price) * 100
            
            # Estimate option price at stop loss level (simplified estimation)
            option_stop_price = current_price * 0.5  # This is a very simplified estimation
            
            return {
                "primary": {
                    "level": closest_support,
                    "recommendation": f"📉 **${closest_support:.2f}** 📉\n\n• Stock Price Stop Level: ${closest_support:.2f} ({percentage_drop:.1f}% below current price)\n• Based on significant technical support\n• For medium-term options (up to 90 days expiry)\n\n⚠️ Options typically lose 60-80% of value when the stock hits stop level. Consider closing your position if price breaks below this point.",
                    "option_stop_price": option_stop_price,
                    "time_horizon": "swing"  # Default to swing
                }
            }
        else:
            # Fallback for put options
            stop_level = current_price * 1.05
            percentage_rise = 5.0
            
            return {
                "primary": {
                    "level": stop_level,
                    "recommendation": f"📈 **${stop_level:.2f}** 📈\n\n• Stock Price Stop Level: ${stop_level:.2f} ({percentage_rise:.1f}% above current price)\n• Based on standard volatility buffer\n• For medium-term options (up to 90 days expiry)\n\n⚠️ Options typically lose 60-80% of value when the stock hits stop level. Consider closing your position if price breaks above this point.",
                    "option_stop_price": current_price * 0.5,
                    "time_horizon": "swing"  # Default to swing
                }
            }

def get_stop_loss_recommendations(ticker_symbol, current_price, option_type, expiration_date=None):
    """
    Wrapper function to maintain backward compatibility with the Discord bot.
    This simply calls get_stop_loss_recommendation and adapts the output format.
    
    Args:
        ticker_symbol: Stock ticker symbol (e.g., 'AAPL')
        current_price: Current stock price
        option_type: 'call' or 'put'
        expiration_date: Option expiration date in YYYY-MM-DD format
        
    Returns:
        Dictionary with stop loss recommendations for different time horizons
    """
    try:
        print(f"DEBUG: get_stop_loss_recommendations called with {ticker_symbol}, {current_price}, {option_type}, {expiration_date}")
        
        # Get stock data
        stock = yf.Ticker(ticker_symbol)
        
        # Call the main recommendation function
        result = get_stop_loss_recommendation(stock, current_price, option_type, expiration_date)
        
        # Adapt the output format for the Discord bot
        # The bot expects a dictionary with keys for each time horizon
        adapted_result = {}
        
        # Extract the trade horizon
        trade_horizon = result.get("trade_horizon", "swing")
        adapted_result["trade_horizon"] = trade_horizon
        
        # If enhanced stop loss exists, include it in the adapted result
        if "enhanced" in result:
            adapted_result["enhanced"] = result["enhanced"]
            # Note: This is the pattern-based stop loss recommendation
            print(f"DEBUG: Enhanced stop loss found and included in adapted result")
        
        # Add specific time horizon recommendations if they exist in the result
        if "scalp" in result:
            adapted_result["scalp"] = result["scalp"]
        
        if "swing" in result:
            adapted_result["swing"] = result["swing"]
        
        if "longterm" in result:
            adapted_result["longterm"] = result["longterm"]
        
        # If we have a primary recommendation but no specific time horizon recommendation,
        # add it to the appropriate time horizon
        if "primary" in result and result["primary"]:
            primary_horizon = result["primary"].get("time_horizon", trade_horizon)
            if primary_horizon == "multiple":
                # If it's a multiple recommendation, add it to all time horizons
                if "scalp" not in adapted_result:
                    adapted_result["scalp"] = result["primary"]
                
                if "swing" not in adapted_result:
                    adapted_result["swing"] = result["primary"]
                
                if "longterm" not in adapted_result:
                    adapted_result["longterm"] = result["primary"]
            else:
                # Otherwise, add it to the specific time horizon
                adapted_result[primary_horizon] = result["primary"]
        
        print(f"DEBUG: Adapted result: {adapted_result}")
        return adapted_result
        
    except Exception as e:
        print(f"Error in get_stop_loss_recommendations wrapper: {str(e)}")
        
        # Return a simple default recommendation structure as fallback
        return {
            "trade_horizon": "swing",
            "swing": {
                "level": current_price * 0.95 if option_type.lower() == 'call' else current_price * 1.05,
                "recommendation": f"📊 **Stop Loss Recommendation** 📊\n\nExit position if the stock price {'falls below' if option_type.lower() == 'call' else 'rises above'} {current_price * 0.95:.2f if option_type.lower() == 'call' else current_price * 1.05:.2f}.",
                "option_stop_price": current_price * 0.5,
                "time_horizon": "swing"
            }
        }
