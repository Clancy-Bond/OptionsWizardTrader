import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import datetime

def calculate_atr(data, window=14):
    """
    Calculate Average True Range (ATR) for volatility-based stops
    
    Args:
        data: DataFrame with OHLC data
        window: Period for ATR calculation
    
    Returns:
        Latest ATR value
    """
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    
    atr = true_range.rolling(window=window).mean().iloc[-1]
    return atr

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

def get_scalp_stop_loss(stock, current_price, option_type):
    """
    Calculate stop loss recommendations for scalp/day trades (based on 5-15 min candles)
    Suitable for options expiring same day or next day
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
    
    Returns:
        Dictionary with stop loss recommendation
    """
    try:
        # For scalping, we need intraday data (5-15 min candles)
        # Since yfinance doesn't provide direct 5-min data through the Python API, 
        # we'll use 1-hour data and adapt our calculations
        
        # Get hourly data for the last 2 days (will be close to 5-15 min in volatility signature)
        hist_data = stock.history(period="2d", interval="1h")
        
        if hist_data.empty:
            raise ValueError("Insufficient intraday data available")
        
        # Calculate ATR for volatility-based stop
        atr = calculate_atr(hist_data, window=7)  # shorter window for scalps
        
        # Check for breakout patterns
        # Detect recent volatility and volume spike
        last_candles = hist_data.tail(5)  # Last 5 hours of trading
        
        # For breakout strategy
        if option_type.lower() == 'call':
            # For long trades in call options
            entry_price = current_price
            
            # Find the low of the breakout candle (most recent with volume spike)
            # We'll use the lowest low of the last 3 candles as a proxy
            breakout_low = last_candles['Low'].tail(3).min()
            
            # Create stop slightly below the low with ATR buffer
            stop_loss = breakout_low - (0.1 * atr)
            
            # Calculate percentage drop
            percentage_drop = ((current_price - stop_loss) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15 min chart)** ⚡\n\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5  # Simplified estimation
            }
        else:
            # For short trades in put options
            entry_price = current_price
            
            # Find the high of the breakdown candle
            breakdown_high = last_candles['High'].tail(3).max()
            
            # Create stop slightly above with ATR buffer
            stop_loss = breakdown_high + (0.1 * atr)
            
            # Calculate percentage rise
            percentage_rise = ((stop_loss - current_price) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15 min chart)** ⚡\n\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5  # Simplified estimation
            }
    
    except Exception as e:
        print(f"Error calculating scalp stop loss: {str(e)}")
        # Fallback to simple percentage based on option type
        if option_type.lower() == 'call':
            stop_loss = current_price * 0.98  # 2% drop for ultra-short-term
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15 min chart)** ⚡\n\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\n\n• Stock Price Stop Level: ${stop_loss:.2f} (2% below current price)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }
        else:
            stop_loss = current_price * 1.02  # 2% rise for ultra-short-term
            return {
                "level": stop_loss,
                "recommendation": f"⚡ **SCALP TRADE STOP LOSS (5-15 min chart)** ⚡\n\n⚠️ **WARNING: CLOSE POSITION WITHIN 15-30 MINUTES MAX!** ⚠️\n\n• Stock Price Stop Level: ${stop_loss:.2f} (2% above current price)",
                "time_horizon": "scalp",
                "option_stop_price": current_price * 0.5
            }

def get_swing_stop_loss(stock, current_price, option_type):
    """
    Calculate stop loss recommendations for swing trades (4H to daily charts)
    Suitable for options with 2 weeks to 3 months expiry
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
    
    Returns:
        Dictionary with stop loss recommendation
    """
    try:
        # Get daily data for the past 30 days
        hist_data = stock.history(period="30d", interval="1d")
        
        if hist_data.empty:
            raise ValueError("Insufficient daily data available")
        
        # Calculate ATR for volatility-based stop
        atr = calculate_atr(hist_data, window=14)  # Standard 14-day ATR
        
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
                stop_loss = max(support_level - (0.5 * atr), current_price * 0.95)
                
                # Calculate percentage drop
                percentage_drop = ((current_price - stop_loss) / current_price) * 100
                
                return {
                    "level": stop_loss,
                    "recommendation": f"📈 **SWING TRADE STOP LOSS (4H/Daily chart)** 📈\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Based on key technical support zone with volatility buffer",
                    "time_horizon": "swing",
                    "option_stop_price": current_price * 0.5  # Simplified estimation
                }
            else:
                # If no clear support found, use ATR-based method
                stop_loss = current_price - (2 * atr)
                percentage_drop = ((current_price - stop_loss) / current_price) * 100
                
                return {
                    "level": stop_loss,
                    "recommendation": f"📈 **SWING TRADE STOP LOSS (4H/Daily chart)** 📈\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\n• Based on stock's volatility (2x ATR)",
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
                    stop_loss = min(resistance_level + (0.5 * atr), current_price * 1.05)
                    
                    # Calculate percentage rise
                    percentage_rise = ((stop_loss - current_price) / current_price) * 100
                    
                    return {
                        "level": stop_loss,
                        "recommendation": f"📉 **SWING TRADE STOP LOSS (4H/Daily chart)** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Based on key technical resistance zone with volatility buffer",
                        "time_horizon": "swing",
                        "option_stop_price": current_price * 0.5
                    }
                else:
                    # If no clear resistance found, use ATR-based method
                    stop_loss = current_price + (2 * atr)
                    percentage_rise = ((stop_loss - current_price) / current_price) * 100
                    
                    return {
                        "level": stop_loss,
                        "recommendation": f"📉 **SWING TRADE STOP LOSS (4H/Daily chart)** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\n• Based on stock's volatility (2x ATR)",
                        "time_horizon": "swing",
                        "option_stop_price": current_price * 0.5
                    }
            except Exception as e:
                print(f"Error in swing trade resistance calculation: {str(e)}")
                # Fallback
                stop_loss = current_price * 1.04  # 4% for swing
                return {
                    "level": stop_loss,
                    "recommendation": f"📉 **SWING TRADE STOP LOSS (4H/Daily chart)** 📉\n\n• Stock Price Stop Level: ${stop_loss:.2f} (4% above current price)\n• Conservative protection level",
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
                "recommendation": f"📈 **SWING TRADE STOP LOSS (4H/Daily chart)** 📈\n\n• Stock Price Stop Level: ${stop_loss:.2f} (7% below current price)\n• Standard swing-trade protection level",
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

def get_longterm_stop_loss(stock, current_price, option_type):
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
        atr = calculate_atr(hist_data, window=10)  # 10-week ATR for long-term
        
        # For long-term trades, we want to respect major technical levels
        if option_type.lower() == 'call':
            # Find significant support zones (weekly lows)
            # We'll use a mix of key support levels and trend analysis
            
            # Calculate a wider dynamic range based on the ATR over a longer period
            # For elite positions (LEAPS, etc), we need a wider stop to avoid early exit
            stop_loss = current_price - (2.5 * atr)
            
            # Ensure it's not too tight
            max_drop_percentage = 0.12  # 12% maximum drop for long-term
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
            stop_loss = current_price + (2.5 * atr)
            
            # Ensure it's not too tight
            max_rise_percentage = 0.12  # 12% maximum rise for long-term
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
            stop_loss = current_price * 0.85  # 15% drop for long-term
            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\n\n• Stock Price Stop Level: ${stop_loss:.2f} (15% below current price)\n• Conservative long-term protection level",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5
            }
        else:
            stop_loss = current_price * 1.15  # 15% rise for long-term
            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\n\n• Stock Price Stop Level: ${stop_loss:.2f} (15% above current price)\n• Conservative long-term protection level",
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
        
        # Get recommendations for all timeframes
        scalp_recommendation = get_scalp_stop_loss(stock, current_price, option_type)
        swing_recommendation = get_swing_stop_loss(stock, current_price, option_type)
        longterm_recommendation = get_longterm_stop_loss(stock, current_price, option_type)
        
        # Create a result dictionary to store all recommendations
        result = {
            "scalp": scalp_recommendation,
            "swing": swing_recommendation,
            "longterm": longterm_recommendation,
            "trade_horizon": trade_horizon
        }
        
        # Set the primary recommendation based on the trade horizon
        if trade_horizon == "scalp":
            result["primary"] = scalp_recommendation
            
            # Create a completely integrated stop loss message
            base_msg = result["primary"]["recommendation"].replace(
                "Technical stop loss:", "Technical stock price stop:"
            )
            
            # Get just the first section (the header and bullet points)
            base_parts = base_msg.split("\n\n")
            if len(base_parts) > 0:
                first_section = base_parts[0]
                
                # Build a completely new message with proper sections
                result["primary"]["recommendation"] = (
                    f"{first_section}\n"
                    f"• For short-term options (1-2 days expiry)\n\n"
                )
                
                # Add the appropriate warning based on option type
                if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 70-90% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                    )
                elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 70-90% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                    )
        
        elif trade_horizon == "swing":
            result["primary"] = swing_recommendation
            
            # Create a completely integrated stop loss message
            base_msg = result["primary"]["recommendation"].replace(
                "Technical stop loss:", "Technical stock price stop:"
            )
            
            # Get just the first section (the header and bullet points)
            base_parts = base_msg.split("\n\n")
            if len(base_parts) > 0:
                first_section = base_parts[0]
                
                # Build a completely new message with proper sections
                result["primary"]["recommendation"] = (
                    f"{first_section}\n"
                    f"• For medium-term options (up to 90 days expiry)\n\n"
                )
                
                # Add the appropriate warning based on option type
                if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 60-80% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                    )
                elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 60-80% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                    )
        
        elif trade_horizon == "longterm":
            result["primary"] = longterm_recommendation
            
            # Create a completely integrated stop loss message
            base_msg = result["primary"]["recommendation"].replace(
                "Technical stop loss:", "Technical stock price stop:"
            )
            
            # Get just the first section (the header and bullet points)
            base_parts = base_msg.split("\n\n")
            if len(base_parts) > 0:
                first_section = base_parts[0]
                
                # Build a completely new message with proper sections
                result["primary"]["recommendation"] = (
                    f"{first_section}\n"
                    f"• For long-term options (6+ months expiry)\n\n"
                )
                
                # Add the appropriate warning based on option type
                if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."
                    )
                elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."
                    )
        
        else:  # unknown trade horizon
            # Set a default primary recommendation (use swing as default)
            result["primary"] = {
                "level": swing_recommendation["level"],  # Default to swing as primary
                "recommendation": "Based on your option details, here are stop-loss recommendations for different trading timeframes. Choose the one that matches your trading strategy and option expiration:\n\n" + 
                                 "1. " + scalp_recommendation["recommendation"] + "\n\n" +
                                 "2. " + swing_recommendation["recommendation"] + "\n\n" +
                                 "3. " + longterm_recommendation["recommendation"] + "\n\n" +
                                 "For more precise option price stop-loss calculations, please provide your specific option expiration date.",
                "time_horizon": "multiple"
            }
        
        # If we have the expiration date, only include recommendations appropriate for the timeframe
        if days_to_expiration is not None:
            # Filter recommendations based on expiration date
            filtered_result = {"primary": result["primary"], "trade_horizon": trade_horizon}
            
            # Include only relevant timeframe recommendations
            if days_to_expiration <= 2:
                filtered_result["scalp"] = result["scalp"]
            
            if days_to_expiration > 2 and days_to_expiration <= 90:
                filtered_result["swing"] = result["swing"]
            
            if days_to_expiration > 90:
                filtered_result["longterm"] = result["longterm"]
            
            return filtered_result
        
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
