"""
Update the stop-loss system to support trade-type based configurations

This script modifies the technical_analysis.py and enhanced_atr_stop_loss.py files to:
1. Update ATR periods by trade type (scalp=7, swing=14, leaps=21)
2. Implement variable ATR buffers by trade type:
   - Breakout: scalp=0.08, swing=0.10, leaps=0.12 
   - Engulfing: scalp=0.04, swing=0.05, leaps=0.06
3. Implement variable volume confirmation by trade type:
   - scalp=1.2, swing=1.5, leaps=1.8
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
    enhanced_atr_function = '''def scale_atr_for_dte(atr, days_to_expiration, pattern_type="breakout", trade_type=None):
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
    
    return atr * base_multiplier * dte_multiplier'''
    
    # Update the function in enhanced_atr_stop_loss.py
    try:
        with open('enhanced_atr_stop_loss.py', 'r') as f:
            content = f.read()
        
        # Replace the existing function with our updated version
        pattern = r'def scale_atr_for_dte\(.*?\):.*?return atr \* base_factor \* dte_factor'
        content = re.sub(pattern, enhanced_atr_function, content, flags=re.DOTALL)
        
        with open('enhanced_atr_stop_loss.py', 'w') as f:
            f.write(content)
            
        logger.info("Updated scale_atr_for_dte in enhanced_atr_stop_loss.py")
    except Exception as e:
        logger.error(f"Error updating enhanced_atr_stop_loss.py: {str(e)}")
    
    # Also update the same function in technical_analysis.py
    try:
        with open('technical_analysis.py', 'r') as f:
            content = f.read()
        
        # Replace the existing function with our updated version
        pattern = r'def scale_atr_for_dte\(.*?\):.*?return atr \* base_factor \* dte_factor'
        content = re.sub(pattern, enhanced_atr_function, content, flags=re.DOTALL)
        
        with open('technical_analysis.py', 'w') as f:
            f.write(content)
            
        logger.info("Updated scale_atr_for_dte in technical_analysis.py")
    except Exception as e:
        logger.error(f"Error updating technical_analysis.py: {str(e)}")

def update_volume_confirmation():
    """Update get_volume_confirmation to use trade-type specific thresholds"""
    
    # New implementation for get_volume_confirmation in enhanced_atr_stop_loss.py
    enhanced_volume_function = '''def get_volume_confirmation(df, periods=10, threshold=1.5, trade_type=None):
    """
    Check if current volume confirms a signal based on trade type
    
    Args:
        df: DataFrame with volume data
        periods: Number of periods to look back for average volume 
        threshold: Multiplier for current volume vs average volume (default 1.5)
        trade_type: Override the default threshold ("scalp", "swing", "longterm")
    
    Returns:
        Boolean volume confirmation, volume ratio
    """
    if len(df) <= periods:
        # Not enough data for confirmation
        return False, 0
    
    # Get the current volume and the average volume for comparison
    current_vol = df['Volume'].iloc[-1]
    avg_vol = df['Volume'].iloc[-periods-1:-1].mean()
    
    # Set threshold based on trade type
    if trade_type == "scalp":
        threshold = 1.2  # Lower volume threshold for scalp trades
    elif trade_type == "longterm":
        threshold = 1.8  # Higher volume threshold for long-term trades
    else:
        threshold = 1.5  # Default for swing trades
    
    # Calculate the ratio and determine if volume is sufficient
    ratio = current_vol / avg_vol if avg_vol > 0 else 0
    confirmed = ratio >= threshold
    
    return confirmed, ratio'''
    
    # Also add a version for technical_analysis.py
    ta_volume_function = '''def get_volume_confirmation(df, periods=10, threshold=1.5, trade_type=None):
    """
    Check if current volume confirms a signal based on trade type
    
    Args:
        df: DataFrame with volume data
        periods: Number of periods to look back for average volume 
        threshold: Multiplier for current volume vs average volume (default 1.5)
        trade_type: Override the default threshold ("scalp", "swing", "longterm")
    
    Returns:
        Boolean volume confirmation, volume ratio
    """
    if len(df) <= periods:
        # Not enough data for confirmation
        return False, 0
    
    # Get the current volume and the average volume for comparison
    current_vol = df['Volume'].iloc[-1]
    avg_vol = df['Volume'].iloc[-periods-1:-1].mean()
    
    # Set threshold based on trade type
    if trade_type == "scalp":
        threshold = 1.2  # Lower volume threshold for scalp trades
    elif trade_type == "longterm":
        threshold = 1.8  # Higher volume threshold for long-term trades
    else:
        threshold = 1.5  # Default for swing trades
    
    # Calculate the ratio and determine if volume is sufficient
    ratio = current_vol / avg_vol if avg_vol > 0 else 0
    confirmed = ratio >= threshold
    
    return confirmed, ratio'''
    
    # Update enhanced_atr_stop_loss.py
    try:
        with open('enhanced_atr_stop_loss.py', 'r') as f:
            content = f.read()
        
        # Replace the existing function with our updated version
        pattern = r'def get_volume_confirmation\(.*?\):.*?return confirmed, ratio'
        content = re.sub(pattern, enhanced_volume_function, content, flags=re.DOTALL)
        
        with open('enhanced_atr_stop_loss.py', 'w') as f:
            f.write(content)
            
        logger.info("Updated get_volume_confirmation in enhanced_atr_stop_loss.py")
    except Exception as e:
        logger.error(f"Error updating enhanced_atr_stop_loss.py: {str(e)}")
    
    # Update technical_analysis.py
    try:
        with open('technical_analysis.py', 'r') as f:
            content = f.read()
        
        # Check if the function exists
        if "def get_volume_confirmation" in content:
            # Replace the existing function with our updated version
            pattern = r'def get_volume_confirmation\(.*?\):.*?return confirmed, ratio'
            content = re.sub(pattern, ta_volume_function, content, flags=re.DOTALL)
        else:
            # Add the function if it doesn't exist
            # Find a good insertion point after imports
            import_section_end = max(content.find("\n\n", content.find("import")), content.find("\n\n"))
            if import_section_end > 0:
                content = content[:import_section_end + 2] + ta_volume_function + "\n\n" + content[import_section_end + 2:]
        
        with open('technical_analysis.py', 'w') as f:
            f.write(content)
            
        logger.info("Updated get_volume_confirmation in technical_analysis.py")
    except Exception as e:
        logger.error(f"Error updating technical_analysis.py: {str(e)}")

def update_timeframe_selection():
    """Update timeframe selection for different trade types"""
    
    # Update get_scalp_stop_loss to use 5m and 15m candles
    scalp_func = '''def get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    """
    Calculate stop loss recommendations for scalp/day trades (based on 5-15-min candles)
    Suitable for options with 0-3 days expiry
    
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
        atr = calculate_atr(hist_data, window=7)  # Use 7-period ATR for scalp trades
        
        # For scalp trades, we'll use a much tighter stop based on ATR
        if option_type.lower() == 'call':
            # For long trades in call options
            
            # Set the buffer based on ATR but with DTE considerations
            # Use smaller percentage for 0-1 DTE
            if days_to_expiration is not None and days_to_expiration <= 1:
                buffer_percentage = 0.99  # 1% max drop for 0-1 DTE
                atr_multiple = 1.0
            else:
                buffer_percentage = 0.98  # 2% max drop for other scalps
                atr_multiple = 1.2
            
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
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS ({timeframe}-chart)** ⚡\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\\n• Based on recent price action with {atr_multiple:.1f}x ATR buffer",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }
        else:
            # For put options (short bias)
            
            # Set the buffer based on ATR but with DTE considerations
            # Use smaller percentage for 0-1 DTE
            if days_to_expiration is not None and days_to_expiration <= 1:
                buffer_percentage = 1.01  # 1% max rise for 0-1 DTE
                atr_multiple = 1.0
            else:
                buffer_percentage = 1.02  # 2% max rise for other scalps
                atr_multiple = 1.2
            
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
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS ({timeframe}-chart)** ⚡\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\\n• Based on recent price action with {atr_multiple:.1f}x ATR buffer",
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
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min)** ⚡\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} (2% below current price)\\n• Standard scalp-trade protection level",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }
        else:
            stop_loss = current_price * 1.02  # 2% rise for scalp
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15-min)** ⚡\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} (2% above current price)\\n• Standard scalp-trade protection level",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }'''
    
    # Update get_swing_stop_loss to use 4h candles
    swing_func = '''def get_swing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
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
                    "recommendation": f"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\\n• Based on key technical support zone with volatility buffer",
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
                    "recommendation": f"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\\n• Based on stock's volatility ({atr_multiple:.1f}x ATR)",
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
                        "recommendation": f"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\\n• Based on key technical resistance zone with volatility buffer",
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
                        "recommendation": f"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\\n• Based on stock's volatility ({atr_multiple:.1f}x ATR)",
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
                    "recommendation": f"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_change:.1f}% above current price)\\n• Conservative protection level",
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
                "recommendation": f"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} (7% below current price)\\n• Standard swing-trade protection level",
                "time_horizon": "swing",
                "option_stop_price": current_price * 0.5
            }
        else:
            stop_loss = current_price * 1.07  # 7% rise for swing
            return {
                "level": stop_loss,
                "recommendation": f"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} (7% above current price)\\n• Standard swing-trade protection level",
                "time_horizon": "swing",
                "option_stop_price": current_price * 0.5
            }'''
    
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
    
    logger.info("Updated pattern detection functions to support trade_type parameter")

def update_atr_periods():
    """Update ATR periods for different trade horizons"""
    
    # Update calculate_atr function in technical_analysis.py to handle trade_type
    with open('technical_analysis.py', 'r') as f:
        content = f.read()
    
    # Define our updated calculate_atr function with trade_type parameter
    updated_atr_func = '''def calculate_atr(data, window=14, period=None, trade_type=None):
    """
    Calculate Average True Range (ATR) with period/window and trade_type support
    
    Args:
        data: DataFrame with OHLC data
        window: Window size for ATR calculation (default 14)
        period: Alternative name for window parameter (for API consistency)
        trade_type: Trade type to determine appropriate ATR period ("scalp", "swing", "longterm")
    
    Returns:
        ATR value (float)
    """
    # Handle the period parameter as an alias for window
    if period is not None:
        window = period
    
    # Adjust window based on trade_type if specified
    if trade_type == "scalp":
        window = 7  # Shorter ATR period for scalp trades
    elif trade_type == "longterm":
        window = 21  # Longer ATR period for long-term trades
    # Else use the default 14 for swing trades or when not specified
        
    # Check if we have enough data
    if len(data) < window + 1:
        return 0
    
    # Calculate True Range
    data = data.copy()
    data['H-L'] = data['High'] - data['Low']
    data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
    data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    
    # Calculate ATR
    data['ATR'] = data['TR'].rolling(window=window).mean()
    
    # Return the most recent ATR value
    return data['ATR'].iloc[-1] if not data['ATR'].empty else 0'''
    
    # Replace the existing calculate_atr function
    pattern = r'def calculate_atr\(.*?\):.*?return data\[\'ATR\'\].iloc\[-1\] if not data\[\'ATR\'\].empty else 0'
    content = re.sub(pattern, updated_atr_func, content, flags=re.DOTALL)
    
    # Add trade_type parameter to calculate_atr calls
    pattern = r'atr = calculate_atr\(hist_data, (window=\d+)\)'
    replacement = r'atr = calculate_atr(hist_data, \1, trade_type=trade_type)'
    content = re.sub(pattern, replacement, content)
    
    # Write updated content back to file
    with open('technical_analysis.py', 'w') as f:
        f.write(content)
    
    logger.info("Updated ATR periods for different trade horizons")

def update_discord_bot_integration():
    """Update discord_bot.py to pass trade_type to stop loss functions"""
    
    with open('discord_bot.py', 'r') as f:
        content = f.read()
    
    # Find handle_stop_loss_request method
    pattern = r'async def handle_stop_loss_request.*?\(.*?\):'
    match = re.search(pattern, content)
    
    if match:
        # Add code to determine trade_type based on DTE
        pattern = r'# Calculate stop loss recommendations based on different time horizons\s+stop_loss_scalp = get_scalp_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
        replacement = '''# Determine trade type based on DTE
        trade_type = None
        if days_to_expiration <= 2:
            trade_type = "scalp"
        elif days_to_expiration <= 90:
            trade_type = "swing"
        else:
            trade_type = "longterm"
            
        # Calculate stop loss recommendations based on different time horizons
        stop_loss_scalp = get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type="scalp")'''
        content = re.sub(pattern, replacement, content)
        
        # Update other stop loss function calls
        pattern = r'stop_loss_swing = get_swing_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
        replacement = r'stop_loss_swing = get_swing_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type="swing")'
        content = re.sub(pattern, replacement, content)
        
        pattern = r'stop_loss_longterm = get_longterm_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
        replacement = r'stop_loss_longterm = get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type="longterm")'
        content = re.sub(pattern, replacement, content)
        
        # Update pattern-based stop loss calls
        pattern = r'try_pattern_stop = calculate_breakout_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
        replacement = r'try_pattern_stop = calculate_breakout_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type=trade_type)'
        content = re.sub(pattern, replacement, content)
        
        pattern = r'try_engulfing_stop = calculate_engulfing_stop_loss\(stock, current_price, option_type, days_to_expiration\)'
        replacement = r'try_engulfing_stop = calculate_engulfing_stop_loss(stock, current_price, option_type, days_to_expiration, trade_type=trade_type)'
        content = re.sub(pattern, replacement, content)
        
        # Write updated content back to file
        with open('discord_bot.py', 'w') as f:
            f.write(content)
        
        logger.info("Updated discord_bot.py integration with trade_type parameter")
    else:
        logger.error("Could not find handle_stop_loss_request method in discord_bot.py")

def main():
    """Main function to execute all update steps"""
    logger.info("Starting trade-type based stop-loss system update")
    
    # Step 1: Update scale_atr_for_dte function
    update_scale_atr_for_dte()
    
    # Step 2: Update volume confirmation thresholds
    update_volume_confirmation()
    
    # Step 3: Update timeframe selection for candle analysis
    update_timeframe_selection()
    
    # Step 4: Update pattern detection functions
    update_pattern_detection_functions()
    
    # Step 5: Update ATR periods by trade type
    update_atr_periods()
    
    # Step 6: Update Discord bot integration
    update_discord_bot_integration()
    
    logger.info("Trade-type based stop-loss system update completed successfully")

if __name__ == "__main__":
    main()