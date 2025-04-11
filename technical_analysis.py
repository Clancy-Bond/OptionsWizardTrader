import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from combined_scalp_stop_loss import calculate_scalp_stop_loss

def calculate_atr(ticker, timeframe):
    """
    Calculate the Average True Range (ATR) for a given ticker and timeframe
    
    Args:
        ticker (str): The ticker symbol
        timeframe (str): The timeframe for the ATR calculation ('1d', '4h', '5m', etc.)
    
    Returns:
        float: The ATR value
    """
    # Map timeframe to yfinance interval and period
    if timeframe == 'weekly':
        interval = '1wk'
        period = '1y'
    elif timeframe == '4h':
        interval = '1h'  # Closest we can get with yfinance
        period = '1mo'
    elif timeframe == '5m':
        interval = '5m'
        period = '5d'
    else:
        interval = '1d'
        period = '1mo'
    
    # Get historical data
    data = yf.download(ticker, period=period, interval=interval, progress=False)
    
    # Calculate ATR
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=14).mean().iloc[-1]
    
    return atr

def get_dte(expiry):
    """Calculate days to expiration"""
    if not expiry:
        return 30  # Default to 30 days if no expiry provided
    
    # Parse the expiry date
    try:
        # Try different date formats
        try:
            expiry_date = datetime.datetime.strptime(expiry, '%m/%d/%Y').date()
        except ValueError:
            try:
                expiry_date = datetime.datetime.strptime(expiry, '%m-%d-%Y').date()
            except ValueError:
                try:
                    expiry_date = datetime.datetime.strptime(expiry, '%d %b %Y').date()
                except ValueError:
                    # If all fail, try to extract year
                    if len(expiry.split('/')[-1]) == 2:
                        expiry = expiry.replace(expiry.split('/')[-1], '20' + expiry.split('/')[-1])
                    expiry_date = datetime.datetime.strptime(expiry, '%m/%d/%Y').date()
        
        # Calculate days to expiration
        today = datetime.date.today()
        dte = (expiry_date - today).days
        return max(0, dte)  # Ensure DTE is not negative
    except Exception:
        return 30  # Default if parsing fails

def get_trade_horizon(dte):
    """Determine trade horizon based on days to expiration"""
    if dte >= 180:
        return "LONG-TERM 📅", "weekly"
    elif dte >= 3:
        return "SWING ⏱️", "4h"
    else:
        return "SCALP ⚡", "5m"

def get_atr_multiplier(trade_horizon):
    """Get ATR multiplier based on trade horizon"""
    if trade_horizon == "LONG-TERM 📅":
        return 0.1
    elif trade_horizon == "SWING ⏱️":
        return 0.5
    else:
        return 1.0  # For scalp, though we'll use combined approach

def get_buffer_limit(dte):
    """Get maximum allowed buffer percentage based on DTE"""
    if dte <= 1:
        return 0.01  # 1% max buffer
    elif dte == 2:
        return 0.02  # 2% max buffer
    elif dte <= 5:
        return 0.03  # 3% max buffer
    else:
        return 0.05  # 5% max buffer

def calculate_stop_loss(ticker, strike, expiry, option_type):
    """
    Calculate stop-loss recommendation for an options position
    
    Args:
        ticker (str): The ticker symbol
        strike (float): The strike price
        expiry (str): The expiration date
        option_type (str): 'call' or 'put'
    
    Returns:
        dict: Stop-loss recommendation details
    """
    # Default response structure
    response = {
        'ticker': ticker,
        'strike': strike,
        'expiry': expiry,
        'option_type': option_type
    }
    
    # Get current stock price
    try:
        stock = yf.Ticker(ticker)
        current_price = stock.info['regularMarketPrice']
        response['current_stock_price'] = current_price
    except Exception:
        # Fallback to last price if real-time data unavailable
        try:
            data = yf.download(ticker, period='1d', progress=False)
            current_price = data['Close'].iloc[-1]
            response['current_stock_price'] = current_price
        except:
            return {
                **response,
                'error': f"Could not retrieve current price for {ticker}",
                'current_price': 0,
                'stop_loss_price': 0,
                'stop_loss_percentage': 0,
                'trade_horizon': "UNKNOWN",
                'risk_warning': "Unable to determine current market price."
            }
    
    # Get option price (simplified - in production would use real options data)
    # This is a simplified calculation for demo purposes
    dte = get_dte(expiry)
    if option_type == 'call':
        intrinsic = max(0, current_price - strike)
    else:
        intrinsic = max(0, strike - current_price)
    
    # Simple time value approximation based on DTE
    time_value = (current_price * 0.01) * min(dte / 30, 1)
    option_price = intrinsic + time_value
    response['current_price'] = option_price
    
    # Get trade horizon and appropriate timeframe
    trade_horizon, timeframe = get_trade_horizon(dte)
    response['trade_horizon'] = trade_horizon
    
    # Calculate stop-loss level
    if trade_horizon == "SCALP ⚡":
        # Use combined scalp stop-loss for short-term trades
        stock_stop_price = calculate_scalp_stop_loss(ticker, option_type)
    else:
        # Use ATR-based stop for swing and long-term trades
        try:
            atr = calculate_atr(ticker, timeframe)
            atr_multiplier = get_atr_multiplier(trade_horizon)
            atr_buffer = atr * atr_multiplier
            
            if option_type == 'call':
                stock_stop_price = current_price - atr_buffer
            else:
                stock_stop_price = current_price + atr_buffer
        except Exception:
            # Fallback to percentage-based stop if ATR calculation fails
            buffer = get_buffer_limit(dte)
            if option_type == 'call':
                stock_stop_price = current_price * (1 - buffer)
            else:
                stock_stop_price = current_price * (1 + buffer)
    
    # Apply DTE-based buffer limits
    max_buffer = get_buffer_limit(dte)
    current_buffer = abs(stock_stop_price - current_price) / current_price
    
    if current_buffer > max_buffer:
        # Tighten stop if buffer exceeds limit
        if option_type == 'call':
            stock_stop_price = current_price * (1 - max_buffer)
        else:
            stock_stop_price = current_price * (1 + max_buffer)
    
    # Calculate option price at stop level (simplified)
    if option_type == 'call':
        stop_intrinsic = max(0, stock_stop_price - strike)
    else:
        stop_intrinsic = max(0, strike - stock_stop_price)
    
    stop_time_value = time_value * 0.5  # Assume time value decreases by half at stop
    stop_option_price = stop_intrinsic + stop_time_value
    
    # Ensure stop price is not negative or zero
    stop_option_price = max(option_price * 0.1, stop_option_price)
    
    # Calculate stop-loss percentage
    stop_loss_percentage = (option_price - stop_option_price) / option_price * 100
    
    # Add risk warning for high risk trades
    risk_warning = None
    if stop_loss_percentage > 50:
        risk_warning = "High risk trade! Consider using a smaller position size or a tighter stop-loss."
    
    response.update({
        'stop_loss_price': stop_option_price,
        'stop_loss_percentage': stop_loss_percentage,
        'underlying_stop_price': stock_stop_price
    })
    
    if risk_warning:
        response['risk_warning'] = risk_warning
    
    return response
