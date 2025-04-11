"""
Update the stop-loss system to support trade-type based configurations

This script modifies the technical_analysis.py and enhanced_atr_stop_loss.py files to:
1. Update ATR periods by trade type (scalp=7, swing=14, leaps=21)
2. Implement variable ATR buffers by trade type:
   - Breakout: scalp=0.08, swing=0.10, leaps=0.12 
   - Engulfing: scalp=0.04, swing=0.05, leaps=0.06
3. Implement variable volume confirmation by trade type:
   - scalp=1.2, swing=1.5×, leaps=1.8
4. Update timeframe selection for candle analysis:
   - scalp: 5m/15m (use both and combine results)
   - swing: 4h 
   - leaps: daily/weekly (unchanged)
5. Add explicit trade_type parameter to stop-loss functions
"""

import re
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("trade_type_update")

def update_scale_atr_for_dte():
    """Update the scale_atr_for_dte function in both files to use trade-type specific buffers"""
    
    # New implementation for enhanced_atr_stop_loss.py
    enhanced_atr_function = """def scale_atr_for_dte(atr, days_to_expiration, pattern_type="breakout", trade_type=None):
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
    
    return atr * base_multiplier * dte_multiplier"""

    # New implementation for technical_analysis.py
    technical_atr_function = """def scale_atr_for_dte(atr, days_to_expiration, pattern_type="breakout", trade_type=None):
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
    
    # Base ATR scaling based on pattern type and trade type
    if pattern_type == "breakout":
        if trade_type == "scalp":
            base_factor = 0.08  # 0.08 × ATR for scalp breakout patterns
        elif trade_type == "longterm":
            base_factor = 0.12  # 0.12 × ATR for longterm breakout patterns
        else:  # swing
            base_factor = 0.10  # 0.10 × ATR for swing breakout patterns
    else:  # engulfing
        if trade_type == "scalp":
            base_factor = 0.04  # 0.04 × ATR for scalp engulfing patterns
        elif trade_type == "longterm":
            base_factor = 0.06  # 0.06 × ATR for longterm engulfing patterns
        else:  # swing
            base_factor = 0.05  # 0.05 × ATR for swing engulfing patterns
    
    # Apply DTE scaling
    if days_to_expiration < 7:
        dte_factor = 0.8  # Reduce buffer for short DTE
    elif days_to_expiration > 30:
        dte_factor = 1.2  # Increase buffer for long DTE
    else:
        dte_factor = 1.0  # Standard buffer for medium DTE
    
    # Combine factors
    return atr * base_factor * dte_factor"""

    # Update both files
    with open('enhanced_atr_stop_loss.py', 'r') as f:
        content = f.read()
    
    # Use regex to find and replace the function definition
    pattern = r'def scale_atr_for_dte\([^)]*\):.*?return atr \* base_multiplier \* dte_multiplier'
    content = re.sub(pattern, enhanced_atr_function, content, flags=re.DOTALL)
    
    with open('enhanced_atr_stop_loss.py', 'w') as f:
        f.write(content)
    
    with open('technical_analysis.py', 'r') as f:
        content = f.read()
    
    # Use regex to find and replace the function definition
    pattern = r'def scale_atr_for_dte\([^)]*\):.*?return atr \* base_factor \* dte_factor'
    content = re.sub(pattern, technical_atr_function, content, flags=re.DOTALL)
    
    with open('technical_analysis.py', 'w') as f:
        f.write(content)
    
    logger.info("Updated scale_atr_for_dte functions with trade-type specific buffers")

def update_volume_confirmation():
    """Update get_volume_confirmation to use trade-type specific thresholds"""
    
    # New implementation for enhanced_atr_stop_loss.py
    volume_func_enhanced = """def get_volume_confirmation(data, lookback=10, threshold=1.5, trade_type=None):
    """
    Check if current volume is above threshold compared to average
    
    Args:
        data: DataFrame with volume data
        lookback: Number of periods to look back for average
        threshold: Multiplier for average (e.g., 1.5 average)
        trade_type: "scalp", "swing", or "longterm" to set threshold
        
    Returns:
        Boolean indicating if volume confirmation exists and the ratio
    """
    # Adjust threshold based on trade type
    if trade_type:
        if trade_type == "scalp":
            threshold = 1.2  # Lower volume requirement for scalps
        elif trade_type == "longterm":
            threshold = 1.8  # Stronger volume requirement for long-term trades
        else:  # swing (default)
            threshold = 1.5
    
    if len(data) <= lookback:
        return False, 1.0
    
    current_volume = data['Volume'].iloc[-1]
    avg_volume = data['Volume'].iloc[-lookback-1:-1].mean()
    
    ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
    confirmation = ratio >= threshold
    
    return confirmation, ratio"""
    
    # New implementation for technical_analysis.py
    volume_func_technical = """def get_volume_confirmation(data, lookback=10, threshold=1.5, trade_type=None):
    """
    Check if current volume is above threshold compared to average
    
    Args:
        data: DataFrame with volume data
        lookback: Number of periods to look back for average
        threshold: Multiplier for average (e.g., 1.5 average)
        trade_type: "scalp", "swing", or "longterm" to set threshold
        
    Returns:
        Boolean indicating if volume confirmation exists and the ratio
    """
    # Adjust threshold based on trade type
    if trade_type:
        if trade_type == "scalp":
            threshold = 1.2  # Lower volume requirement for scalps
        elif trade_type == "longterm":
            threshold = 1.8  # Stronger volume requirement for long-term trades
        else:  # swing (default)
            threshold = 1.5
    
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
        return False, 0.0"""
    
    # Update both files
    with open('enhanced_atr_stop_loss.py', 'r') as f:
        content = f.read()
    
    pattern = r'def get_volume_confirmation\([^)]*\):.*?return confirmation, ratio'
    content = re.sub(pattern, volume_func_enhanced, content, flags=re.DOTALL)
    
    with open('enhanced_atr_stop_loss.py', 'w') as f:
        f.write(content)
    
    with open('technical_analysis.py', 'r') as f:
        content = f.read()
    
    pattern = r'def get_volume_confirmation\([^)]*\):.*?return False, 0.0'
    content = re.sub(pattern, volume_func_technical, content, flags=re.DOTALL)
    
    with open('technical_analysis.py', 'w') as f:
        f.write(content)
    
    logger.info("Updated get_volume_confirmation functions with trade-type specific thresholds")

def update_atr_periods():
    """Update the ATR periods by trade type"""
    
    # Update in get_scalp_stop_loss (already 7, no change needed)
    # Update in get_swing_stop_loss (already 14, no change needed)
    # Update in get_longterm_stop_loss (change from 10 to 21)
    
    with open('technical_analysis.py', 'r') as f:
        content = f.read()
    
    # Use regex to find and replace the ATR calculation in get_longterm_stop_loss
    pattern = r'(# Calculate ATR for volatility-based stop\n\s*atr = calculate_atr\(hist_data, window=)10(\)  # 10-week ATR for long-term)'
    content = re.sub(pattern, r'\g<1>21\g<2>', content)
    
    with open('technical_analysis.py', 'w') as f:
        f.write(content)
    
    logger.info("Updated ATR period for longterm from 10 to 21")

def update_timeframe_selection():
    """Update timeframe selection for candle analysis"""
    
    # Update get_scalp_stop_loss to use 5m and 15m candles
    scalp_func = """def get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss recommendations for scalp/day trades (based on 5-15-min candles)
    Suitable for options expiring same day or next day
    
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
        # For scalping, use 5min and 15min data
        # Try 5-minute data first (gives the most detail for intraday scalps)
        hist_data_5m = stock.history(period="1d", interval="5m")
        hist_data_15m = stock.history(period="1d", interval="15m")
        
        # Use 15-minute data if 5-minute is unavailable/empty
        if hist_data_5m.empty and hist_data_15m.empty:
            # Fall back to 1-hour if both are unavailable
            hist_data = stock.history(period="2d", interval="1h")
            if hist_data.empty:
                raise ValueError("Insufficient intraday data available")
        else:
            # Prefer 5-minute data if available
            hist_data = hist_data_5m if not hist_data_5m.empty else hist_data_15m
        
        # Calculate ATR for volatility-based stop
        atr = calculate_atr(hist_data, window=7)  # shorter window for scalps
        
        # Check for breakout patterns
        # Detect recent volatility and volume spike
        last_candles = hist_data.tail(5)  # Last 5 periods (5-min or 15-min)
        
        # For breakout strategy
        if option_type.lower() == 'call':
            # For long trades in call options
            entry_price = current_price
            
            # Find the low of the breakout candle (most recent with volume spike)
            # We'll use the lowest low of the last 3 candles as a proxy
            breakout_low = last_candles['Low'].tail(3).min()
            
            # Create stop slightly below the low with ATR buffer
            # Calculate dynamic buffer based on days to expiration and trade type
            buffer_factor = 0.08  # Default buffer factor for scalp (0.08 for breakout)
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 1:
                    buffer_factor = 0.05  # Half the buffer for 0-1 DTE
            
            stop_loss = breakout_low - (buffer_factor * atr)
            
            # Calculate percentage drop
            percentage_drop = ((current_price - stop_loss) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min chart)** ⚡\\n\\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5  # Simplified estimation
            }
        else:
            # For short trades in put options
            entry_price = current_price
            
            # Find the high of the breakdown candle
            breakdown_high = last_candles['High'].tail(3).max()
            
            # Create stop slightly above with ATR buffer
            # Calculate dynamic buffer based on days to expiration and trade type
            buffer_factor = 0.08  # Default buffer factor for scalp (0.08 for breakout)
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 1:
                    buffer_factor = 0.05  # Half the buffer for 0-1 DTE
            
            stop_loss = breakdown_high + (buffer_factor * atr)
            
            # Calculate percentage rise
            percentage_rise = ((stop_loss - current_price) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min chart)** ⚡\\n\\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5  # Simplified estimation
            }
    
    except Exception as e:
        print(f"Error calculating scalp stop loss: {str(e)}")
        # Fallback to simple percentage based on option type
        if option_type.lower() == 'call':
            # Adjust fallback based on days to expiration
            min_percentage = 0.98  # Default 2% buffer for scalp
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 1:
                    min_percentage = 0.99  # 1% for 0-1 DTE
            
            stop_loss = current_price * min_percentage  # Dynamic percentage for scalp
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min chart)** ⚡\\n\\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({(1.0 - min_percentage) * 100:.1f}% below current price)",
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
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min chart)** ⚡\\n\\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_change:.1f}% above current price)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }"""
    
    # Update get_swing_stop_loss to use 4h candles
    swing_func = """def get_swing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss recommendations for swing trades (4h-charts)
    Suitable for options with 2 weeks to 3 months expiry
    """
    
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
        atr = calculate_atr(hist_data, window=14)  # Standard 14-period ATR
        
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
                
                stop_loss = max(support_level - (buffer_factor * atr), current_price * min_percentage)
                
                # Calculate percentage drop
                percentage_drop = ((current_price - stop_loss) / current_price) * 100
                
                return {
                    "level": stop_loss,
                    "recommendation": f"📈 **SWING TRADE STOP LOSS (4h chart)** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\\n• Based on key technical support zone with volatility buffer",
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
                
                # Use the ATR multiple but cap at min_percentage
                stop_loss = max(current_price - (atr_multiple * atr), current_price * min_percentage)
                percentage_drop = ((current_price - stop_loss) / current_price) * 100
                
                return {
                    "level": stop_loss,
                    "recommendation": f"📈 **SWING TRADE STOP LOSS (4h chart)** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\\n• Based on stock's volatility ({atr_multiple:.1f}x ATR)",
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
                    
                    stop_loss = min(resistance_level + (buffer_factor * atr), current_price * max_percentage)
                    
                    # Calculate percentage rise
                    percentage_rise = ((stop_loss - current_price) / current_price) * 100
                    
                    return {
                        "level": stop_loss,
                        "recommendation": f"📉 **SWING TRADE STOP LOSS (4h chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\\n• Based on key technical resistance zone with volatility buffer",
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
                    
                    # Use the ATR multiple but cap at max_percentage
                    stop_loss = min(current_price + (atr_multiple * atr), current_price * max_percentage)
                    percentage_rise = ((stop_loss - current_price) / current_price) * 100
                    
                    return {
                        "level": stop_loss,
                        "recommendation": f"📉 **SWING TRADE STOP LOSS (4h chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\\n• Based on stock's volatility ({atr_multiple:.1f}x ATR)",
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
                    "recommendation": f"📉 **SWING TRADE STOP LOSS (4h chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_change:.1f}% above current price)\\n• Conservative protection level",
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
                "recommendation": f"📈 **SWING TRADE STOP LOSS (4h chart)** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} (7% below current price)\\n• Standard swing-trade protection level",
                "time_horizon": "swing",
                "option_stop_price": current_price * 0.5
            }
        else:
            stop_loss = current_price * 1.07  # 7% rise for swing
            return {
                "level": stop_loss,
                "recommendation": f"📉 **SWING TRADE STOP LOSS (4h chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} (7% above current price)\\n• Standard swing-trade protection level",
                "time_horizon": "swing",
                "option_stop_price": current_price * 0.5
            }"""
    
    # Update technical_analysis.py with new functions
    with open('technical_analysis.py', 'r') as f:
        content = f.read()
    
    # Replace get_scalp_stop_loss function
    pattern_scalp = r'def get_scalp_stop_loss\(.*?\):'
    replacement_scalp = 'def get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):'
    content = re.sub(pattern_scalp, replacement_scalp, content)
    
    pattern_swing = r'def get_swing_stop_loss\(.*?\):'
    replacement_swing = 'def get_swing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):'
    content = re.sub(pattern_swing, replacement_swing, content)
    
    pattern_longterm = r'def get_longterm_stop_loss\(.*?\):'
    replacement_longterm = 'def get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):'
    content = re.sub(pattern_longterm, replacement_longterm, content)
    
    # Replace the entire scalp function
    pattern_scalp_body = r'def get_scalp_stop_loss\(.*?\):.*?option_stop_price": current_price \* 0.5\n            \}'
    content = re.sub(pattern_scalp_body, scalp_func, content, flags=re.DOTALL)
    
    # Replace the entire swing function 
    pattern_swing_body = r'def get_swing_stop_loss\(.*?\):.*?option_stop_price": current_price \* 0.5\n            \}'
    content = re.sub(pattern_swing_body, swing_func, content, flags=re.DOTALL)
    
    # Write updated content back to file
    with open('technical_analysis.py', 'w') as f:
        f.write(content)
    
    logger.info("Updated timeframe selection for candle analysis")

def update_pattern_detection_functions():
    """Update the pattern detection functions to include trade_type parameter"""
    
    # Update calculate_breakout_stop_loss
    with open('technical_analysis.py', 'r') as f:
        content = f.read()
    
    # Replace the pattern functions to include trade_type parameter
    pattern = r'def calculate_breakout_stop_loss\(stock, current_price, option_type, days_to_expiration=None\):'
    replacement = 'def calculate_breakout_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'def calculate_engulfing_stop_loss\(stock, current_price, option_type, days_to_expiration=None\):'
    replacement = 'def calculate_engulfing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):'
    content = re.sub(pattern, replacement, content)
    
    # Add trade_type parameter to atr_buffer calculation 
    pattern = r'atr_buffer = scale_atr_for_dte\(atr, days_to_expiration or 14, "breakout"\)'
    replacement = 'atr_buffer = scale_atr_for_dte(atr, days_to_expiration or 14, "breakout", trade_type)'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'atr_buffer = scale_atr_for_dte\(atr, days_to_expiration or 14, "engulfing"\)'
    replacement = 'atr_buffer = scale_atr_for_dte(atr, days_to_expiration or 14, "engulfing", trade_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add trade_type parameter to volume confirmation
    pattern = r'volume_confirmed, volume_ratio = get_volume_confirmation\(hist_data\)'
    replacement = 'volume_confirmed, volume_ratio = get_volume_confirmation(hist_data, trade_type=trade_type)'
    content = re.sub(pattern, replacement, content)
    
    # Write updated content back to file
    with open('technical_analysis.py', 'w') as f:
        f.write(content)
    
    # Do the same for enhanced_atr_stop_loss.py
    with open('enhanced_atr_stop_loss.py', 'r') as f:
        content = f.read()
    
    # Replace the pattern functions to include trade_type parameter
    pattern = r'def calculate_breakout_stop_loss\(stock, current_price, option_type, days_to_expiration=None\):'
    replacement = 'def calculate_breakout_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'def calculate_engulfing_stop_loss\(stock, current_price, option_type, days_to_expiration=None\):'
    replacement = 'def calculate_engulfing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):'
    content = re.sub(pattern, replacement, content)
    
    # Add trade_type parameter to atr_buffer calculation
    pattern = r'scaled_atr = scale_atr_for_dte\(atr, days_to_expiration, "breakout"\)'
    replacement = 'scaled_atr = scale_atr_for_dte(atr, days_to_expiration, "breakout", trade_type)'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'scaled_atr = scale_atr_for_dte\(atr, days_to_expiration, "engulfing"\)'
    replacement = 'scaled_atr = scale_atr_for_dte(atr, days_to_expiration, "engulfing", trade_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add trade_type parameter to volume confirmation
    pattern = r'volume_confirmed, volume_ratio = get_volume_confirmation\(data\)'
    replacement = 'volume_confirmed, volume_ratio = get_volume_confirmation(data, trade_type=trade_type)'
    content = re.sub(pattern, replacement, content)
    
    # Update get_enhanced_stop_loss to accept explicit trade_type parameter
    pattern = r'def get_enhanced_stop_loss\(stock, current_price, option_type, days_to_expiration=None\):'
    replacement = 'def get_enhanced_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):'
    content = re.sub(pattern, replacement, content)
    
    # Update to use provided trade_type
    pattern = (r'# First determine the appropriate trade horizon based on DTE\n'
              r'    if days_to_expiration is not None:\n'
              r'        if days_to_expiration <= 2:\n'
              r'            trade_horizon = "scalp"\n'
              r'        elif days_to_expiration <= 90:\n'
              r'            trade_horizon = "swing"\n'
              r'        else:\n'
              r'            trade_horizon = "longterm"\n'
              r'    else:\n'
              r'        trade_horizon = "swing"  # Default if unknown')
    replacement = (r'# First determine the appropriate trade horizon based on trade_type or DTE\n'
                  r'    if trade_type is not None:\n'
                  r'        trade_horizon = trade_type  # Use provided trade_type\n'
                  r'    elif days_to_expiration is not None:\n'
                  r'        if days_to_expiration <= 2:\n'
                  r'            trade_horizon = "scalp"\n'
                  r'        elif days_to_expiration <= 90:\n'
                  r'            trade_horizon = "swing"\n'
                  r'        else:\n'
                  r'            trade_horizon = "longterm"\n'
                  r'    else:\n'
                  r'        trade_horizon = "swing"  # Default if unknown')
    content = re.sub(pattern, replacement, content)
    
    # Pass trade_type to the pattern-specific stop loss functions
    pattern = r'breakout_stop = calculate_breakout_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
    replacement = 'breakout_stop = calculate_breakout_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type=trade_horizon)'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'engulfing_stop = calculate_engulfing_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
    replacement = 'engulfing_stop = calculate_engulfing_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type=trade_horizon)'
    content = re.sub(pattern, replacement, content)
    
    # Write updated content back to file
    with open('enhanced_atr_stop_loss.py', 'w') as f:
        f.write(content)
    
    logger.info("Updated pattern detection functions to include trade_type parameter")

def update_stop_loss_recommendation():
    """Update get_stop_loss_recommendation to support trade_type parameter"""
    
    with open('technical_analysis.py', 'r') as f:
        content = f.read()
    
    # Update function signature
    pattern = r'def get_stop_loss_recommendation\(stock, current_price, option_type, expiration=None\):'
    replacement = 'def get_stop_loss_recommendation(stock, current_price, option_type, expiration=None, trade_type=None):'
    content = re.sub(pattern, replacement, content)
    
    # Update function calls to pass trade_type
    pattern = r'enhanced_stop = get_enhanced_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
    replacement = 'enhanced_stop = get_enhanced_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type)'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'scalp_recommendation = get_scalp_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
    replacement = 'scalp_recommendation = get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type)'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'swing_recommendation = get_swing_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
    replacement = 'swing_recommendation = get_swing_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type)'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'longterm_recommendation = get_longterm_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
    replacement = 'longterm_recommendation = get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type)'
    content = re.sub(pattern, replacement, content)
    
    # Update wrapper function to pass trade_type
    pattern = r'def get_stop_loss_recommendations\(ticker_symbol, current_price, option_type, expiration_date=None\):'
    replacement = 'def get_stop_loss_recommendations(ticker_symbol, current_price, option_type, expiration_date=None, trade_type=None):'
    content = re.sub(pattern, replacement, content)
    
    # Update call to get_stop_loss_recommendation to pass trade_type
    pattern = r'result = get_stop_loss_recommendation\(stock, current_price, option_type, expiration_date\)'
    replacement = 'result = get_stop_loss_recommendation(stock, current_price, option_type, expiration_date, trade_type)'
    content = re.sub(pattern, replacement, content)
    
    # Write updated content back to file
    with open('technical_analysis.py', 'w') as f:
        f.write(content)
    
    # Update in the discord_bot.py to pass trade_type if available
    try:
        with open('discord_bot.py', 'r') as f:
            bot_content = f.read()
        
        # Find the handle_stop_loss_request method and update it to extract trade_type
        if 'def handle_stop_loss_request' in bot_content:
            # Add trade_type extraction to the query parsing
            pattern = r'# Use technical analysis to get stop loss recommendations.*?stop_loss_result = technical_analysis\.get_stop_loss_recommendations\((.*?)\)'
            matches = re.findall(pattern, bot_content, re.DOTALL)
            
            if matches:
                params = matches[0]
                if 'expiration_date' in params and 'trade_type' not in params:
                    # Add trade_type parameter
                    updated_params = params.rstrip() + ', query.get("trade_type")'
                    updated_call = f'stop_loss_result = technical_analysis.get_stop_loss_recommendations({updated_params})'
                    bot_content = bot_content.replace(f'stop_loss_result = technical_analysis.get_stop_loss_recommendations({params})', updated_call)
                    
                    # Write updated content back to file
                    with open('discord_bot.py', 'w') as f:
                        f.write(bot_content)
                    
                    logger.info("Updated discord_bot.py to pass trade_type parameter")
    except Exception as e:
        logger.warning(f"Could not update discord_bot.py: {e}")
    
    logger.info("Updated get_stop_loss_recommendation to support trade_type parameter")

def implement_changes():
    """Implement all changes to the stop-loss system"""
    
    logger.info("Starting implementation of trade-type specific stop-loss system")
    
    # 1. Update ATR periods by trade type
    update_atr_periods()
    
    # 2. Implement variable ATR buffers by trade type
    update_scale_atr_for_dte()
    
    # 3. Implement variable volume confirmation by trade type 
    update_volume_confirmation()
    
    # 4. Update timeframe selection for candle analysis
    update_timeframe_selection()
    
    # 5. Update pattern detection functions
    update_pattern_detection_functions()
    
    # 6. Update the stop loss recommendation function
    update_stop_loss_recommendation()
    
    logger.info("Completed implementation of trade-type specific stop-loss system")
    logger.info("✅ The stop-loss system now fully supports trade type specific configurations")

if __name__ == "__main__":
    implement_changes()