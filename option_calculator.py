import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import math
from scipy.stats import norm
from calculate_dynamic_theta_decay import project_theta_decay

# Create a copy of the function in this file if the import fails
def format_ticker_local(ticker):
    """
    Format ticker symbol to be compatible with yfinance.
    
    Args:
        ticker: Ticker symbol input
    
    Returns:
        Formatted ticker symbol
    """
    # Remove any whitespace
    ticker = ticker.strip().upper()
    
    # Replace any special characters except dots
    import re
    ticker = re.sub(r'[^A-Z0-9\.]', '', ticker)
    
    # Check if it's a valid ticker format
    if not ticker or len(ticker) > 10:
        return 'AAPL'  # Default to AAPL if invalid
    
    return ticker

# Try to import format_ticker, but use the local version if it fails
try:
    from utils_file import format_ticker
except ImportError:
    format_ticker = format_ticker_local

def handle_expiration_date_validation(expiration_date, ticker_obj):
    """
    Check if the given expiration date is available and find the closest one if not.
    
    Args:
        expiration_date: The requested expiration date (string in format 'YYYY-MM-DD')
        ticker_obj: The yfinance Ticker object (can be None)
        
    Returns:
        A tuple with (valid_expiration_date, warning_message)
    """
    # Check if valid ticker object was provided
    if ticker_obj is None:
        print("No ticker object provided for expiration date validation")
        return None, "No ticker object available to validate expiration dates"
        
    # Check if the expiration date is available
    available_expirations = ticker_obj.options
    
    # No options data at all
    if not available_expirations:
        return None, f"No options data available. The market may be closed or this ticker might not have options trading."
    
    # Exact match found
    if expiration_date in available_expirations:
        return expiration_date, None
    
    # Find closest available expiration
    requested_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
    closest_date = min(available_expirations, key=lambda x: abs((datetime.strptime(x, '%Y-%m-%d').date() - requested_date).days))
    days_diff = abs((datetime.strptime(closest_date, '%Y-%m-%d').date() - requested_date).days)
    
    if days_diff <= 7:
        # Close enough, just use it
        message = f"Expiration {expiration_date} not found. Using closest available: {closest_date} ({days_diff} days different)"
    else:
        # Quite different, give a more detailed warning
        if datetime.strptime(closest_date, '%Y-%m-%d').date() < requested_date:
            message = f"Expiration {expiration_date} not found. The furthest available expiration is {closest_date}, which is {days_diff} days earlier."
        else:
            message = f"Expiration {expiration_date} not found. The closest available is {closest_date}, which is {days_diff} days later."
    
    return closest_date, message

def get_option_chain(stock, expiration_date, option_type):
    """
    Get the option chain for a given stock, expiration date, and option type.
    
    Args:
        stock: yfinance Ticker object or None
        expiration_date: string in format 'YYYY-MM-DD'
        option_type: 'call' or 'put'
    
    Returns:
        Pandas DataFrame with option chain data
    
    Raises:
        ValueError: If the expiration date is not available
    """
    try:
        # Check if a valid stock object was provided
        if stock is None:
            print("No ticker object provided for option chain lookup")
            return pd.DataFrame()  # Return empty DataFrame
            
        # Validate the expiration date and find the closest one if needed
        validated_expiration, warning_message = handle_expiration_date_validation(expiration_date, stock)
        
        if validated_expiration is None:
            # No options data available at all
            raise ValueError(warning_message)
        
        if warning_message:
            # Expiration date was modified
            print(f"Warning: {warning_message}")
            expiration_date = validated_expiration
        
        # Get the option chain
        options = stock.option_chain(expiration_date)
        
        if option_type.lower() == 'call':
            return options.calls
        else:
            return options.puts
    except Exception as e:
        print(f"Error getting option chain: {str(e)}")
        
        # Re-raise with more context for better error handling upstream
        if "No options data available" in str(e) or "cannot be found" in str(e) or "Expiration" in str(e):
            raise ValueError(str(e))
        
        # For other errors, return empty DataFrame
        return pd.DataFrame()  # Return empty DataFrame on other errors

def get_option_greeks(stock, expiration_date, strike_price, option_type):
    """
    Calculate option Greeks (Delta, Gamma, Theta, Vega) using the Black-Scholes model.
    
    Args:
        stock: yfinance Ticker object or None
        expiration_date: string in format 'YYYY-MM-DD'
        strike_price: option strike price
        option_type: 'call' or 'put'
    
    Returns:
        Dictionary with Greeks values
    """
    try:
        # Check if stock is a valid yfinance Ticker object
        if stock is None:
            print("No ticker object provided for Greeks calculation")
            return None
            
        # Get current stock price
        try:
            current_price = stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
        except Exception as e:
            print(f"Error getting current price: {e}")
            return None
        
        # Get option chain to find implied volatility
        options = stock.option_chain(expiration_date)
        
        if option_type.lower() == 'call':
            chain = options.calls
        else:
            chain = options.puts
        
        # Find the option with the given strike price
        option = chain[chain['strike'] == strike_price]
        
        if option.empty:
            return None
        
        # Extract parameters
        implied_volatility = option['impliedVolatility'].iloc[0]
        
        # Calculate days to expiration
        today = datetime.now().date()
        expiry = datetime.strptime(expiration_date, '%Y-%m-%d').date()
        days_to_expiration = (expiry - today).days
        time_to_expiration = days_to_expiration / 365.0  # Convert to years
        
        # Use a risk-free rate (1-year Treasury Bill rate is approximately 5% as of writing)
        risk_free_rate = 0.05
        
        # Calculate d1 and d2 for Black-Scholes
        d1 = (np.log(current_price / strike_price) + (risk_free_rate + 0.5 * implied_volatility ** 2) * time_to_expiration) / (implied_volatility * np.sqrt(time_to_expiration))
        d2 = d1 - implied_volatility * np.sqrt(time_to_expiration)
        
        # Calculate Greeks
        if option_type.lower() == 'call':
            delta = norm.cdf(d1)
            gamma = norm.pdf(d1) / (current_price * implied_volatility * np.sqrt(time_to_expiration))
            theta = -((current_price * norm.pdf(d1) * implied_volatility) / (2 * np.sqrt(time_to_expiration))) - risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiration) * norm.cdf(d2)
            vega = current_price * np.sqrt(time_to_expiration) * norm.pdf(d1) * 0.01  # Multiply by 0.01 to get the impact of a 1% change in volatility
        else:  # put option
            delta = norm.cdf(d1) - 1
            gamma = norm.pdf(d1) / (current_price * implied_volatility * np.sqrt(time_to_expiration))
            theta = -((current_price * norm.pdf(d1) * implied_volatility) / (2 * np.sqrt(time_to_expiration))) + risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiration) * norm.cdf(-d2)
            vega = current_price * np.sqrt(time_to_expiration) * norm.pdf(d1) * 0.01
        
        # Using the actual option price to adjust the Greek calculations
        option_price = option['lastPrice'].iloc[0]
        
        # Attempt to get more accurate Greeks from the market data
        try:
            options = stock.option_chain(expiration_date)
            if option_type.lower() == 'call':
                chain = options.calls
            else:
                chain = options.puts
                
            exact_option = chain[chain['strike'] == strike_price]
            
            if not exact_option.empty:
                # Some brokers provide these values
                if 'delta' in exact_option.columns:
                    delta = exact_option['delta'].iloc[0]
                if 'gamma' in exact_option.columns:
                    gamma = exact_option['gamma'].iloc[0]
                if 'theta' in exact_option.columns:
                    theta = exact_option['theta'].iloc[0]
                if 'vega' in exact_option.columns:
                    vega = exact_option['vega'].iloc[0]
        except:
            # If fetching exact Greeks fails, continue with calculated values
            pass
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta / 365.0,  # Convert to daily theta
            'vega': vega,
            'implied_volatility': implied_volatility,
            'price': option_price  # Add the option price to the return dictionary
        }
    except Exception as e:
        print(f"Error calculating Greeks: {str(e)}")
        # Provide reasonable default values based on option type
        if option_type.lower() == 'call':
            return {
                'error': 'Unable to retrieve market data for this option',
                'data_available': False
            }
        else:
            return {
                'error': 'Unable to retrieve market data for this option',
                'data_available': False
            }

def calculate_option_price(current_price, target_price, strike_price, greeks, days_to_expiration, option_type):
    """
    Estimate the future option price based on a target stock price using the option Greeks.
    
    Args:
        current_price: Current stock price
        target_price: Target stock price
        strike_price: Option strike price
        greeks: Dictionary with option Greeks
        days_to_expiration: Number of days to option expiration
        option_type: 'call' or 'put'
    
    Returns:
        Estimated option price at the target stock price
    """
    try:
        if not greeks:
            # If Greeks aren't available, use intrinsic value calculation
            if option_type.lower() == 'call':
                intrinsic_value = max(0, target_price - strike_price)
                return intrinsic_value
            else:
                intrinsic_value = max(0, strike_price - target_price)
                return intrinsic_value
        
        # We don't have a ticker, so skip trying to get option chain data
        stock = None
        expiry_date = (datetime.now() + timedelta(days=days_to_expiration)).strftime('%Y-%m-%d')
        # Don't try to get option data without a valid ticker
        
        # We don't have a valid ticker object, so estimate the current option price using intrinsic value
        current_option_price = greeks.get('price', 0)
        if current_option_price == 0:
            # Fallback if price not in greeks dictionary
            if option_type.lower() == 'call':
                current_option_price = max(0, current_price - strike_price)
            else:
                current_option_price = max(0, strike_price - current_price)
        
        # Calculate price change using Greeks
        delta = greeks.get('delta', 0)
        gamma = greeks.get('gamma', 0)
        theta = greeks.get('theta', 0)
        
        # Calculate price change due to stock price movement
        price_change = delta * (target_price - current_price)
        
        # Add adjustment for convexity (gamma)
        gamma_adjustment = 0.5 * gamma * (target_price - current_price) ** 2
        
        # Add adjustment for time decay (theta)
        theta_adjustment = theta * days_to_expiration
        
        # Calculate estimated option price
        estimated_price = current_option_price + price_change + gamma_adjustment + theta_adjustment
        
        # Ensure the option price is never negative
        estimated_price = max(0, estimated_price)
        
        return estimated_price
    except Exception as e:
        print(f"Error calculating option price: {str(e)}")
        # Fallback to intrinsic value calculation
        if option_type.lower() == 'call':
            return max(0, target_price - strike_price)
        else:
            return max(0, strike_price - target_price)

def get_option_price(ticker_symbol, option_type, strike_price, expiration_date):
    """
    Get the current market price for an option.
    
    Args:
        ticker_symbol: Stock ticker symbol (e.g., 'AAPL')
        option_type: 'call' or 'put'
        strike_price: Option strike price
        expiration_date: Expiration date (string in format 'YYYY-MM-DD' or datetime object)
        
    Returns:
        Current option price or estimated price if market data unavailable
    """
    try:
        print(f"Getting option price for {ticker_symbol} {option_type} ${strike_price} expiring {expiration_date}")
        
        # Format the ticker symbol
        ticker_symbol = format_ticker(ticker_symbol)
        
        # Convert expiration date to string if it's a datetime object
        if isinstance(expiration_date, datetime) or isinstance(expiration_date, date):
            expiration_date = expiration_date.strftime('%Y-%m-%d')
        
        # Get the stock data
        stock = yf.Ticker(ticker_symbol)
        current_price = stock.history(period='1d')['Close'].iloc[-1]
        
        # Get option chain
        chain = get_option_chain(stock, expiration_date, option_type)
        
        # Find the option with the closest strike price
        if not chain.empty:
            closest_strike = min(chain['strike'], key=lambda x: abs(x - strike_price))
            option_data = chain[chain['strike'] == closest_strike]
            
            if not option_data.empty:
                # Get the last price
                price = option_data['lastPrice'].iloc[0]
                
                # If the price is very low or zero, use the mid of bid-ask
                if price < 0.05:
                    bid = option_data['bid'].iloc[0]
                    ask = option_data['ask'].iloc[0]
                    if bid > 0 or ask > 0:
                        price = (bid + ask) / 2
                
                # If still zero or very low, use a simplified model to estimate
                if price < 0.02:
                    # Calculate intrinsic value
                    if option_type.lower() == 'call':
                        intrinsic = max(0, current_price - strike_price)
                    else:
                        intrinsic = max(0, strike_price - current_price)
                    
                    # Add a small time value based on days to expiration
                    today = datetime.now().date()
                    expiry = datetime.strptime(expiration_date, '%Y-%m-%d').date()
                    days_to_expiration = max(1, (expiry - today).days)
                    
                    # Simple time value approximation
                    time_value = current_price * 0.01 * (days_to_expiration / 30.0)
                    price = max(0.05, intrinsic + time_value)
                
                return price
            
        # If we couldn't get data from the option chain, estimate
        # Calculate days to expiration
        today = datetime.now().date()
        expiry = datetime.strptime(expiration_date, '%Y-%m-%d').date()
        days_to_expiration = max(1, (expiry - today).days)
        
        # Get volatility from stock
        try:
            hist_data = stock.history(period='1m')
            returns = np.log(hist_data['Close'] / hist_data['Close'].shift(1))
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            
            # Simple Black-Scholes approximation
            T = days_to_expiration / 365.0
            r = 0.05  # Risk-free rate
            
            d1 = (np.log(current_price / strike_price) + (r + 0.5 * volatility**2) * T) / (volatility * np.sqrt(T))
            d2 = d1 - volatility * np.sqrt(T)
            
            if option_type.lower() == 'call':
                price = current_price * norm.cdf(d1) - strike_price * np.exp(-r * T) * norm.cdf(d2)
            else:
                price = strike_price * np.exp(-r * T) * norm.cdf(-d2) - current_price * norm.cdf(-d1)
                
            return max(0.05, price)
            
        except Exception as e:
            print(f"Error estimating option price: {str(e)}")
            
            # Fallback to intrinsic value plus small time premium
            if option_type.lower() == 'call':
                intrinsic = max(0, current_price - strike_price)
            else:
                intrinsic = max(0, strike_price - current_price)
                
            # Add a small time value based on DTE
            time_value = current_price * 0.01 * (days_to_expiration / 30.0)
            return max(0.05, intrinsic + time_value)
            
    except Exception as e:
        print(f"Error in get_option_price: {str(e)}")
        return 0.05  # Return a minimal price as fallback
