import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import math
from scipy.stats import norm
from utils_file import format_ticker

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
        if option_type.lower() == 'call':
            current_option_price = max(0, current_price - strike_price)
        else:
            current_option_price = max(0, strike_price - current_price)
        
        # Calculate price change using Greeks
        delta = greeks['delta']
        gamma = greeks['gamma']
        theta = greeks['theta']
        
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
            hist_data = stock.history(period='1mo')
            if not hist_data.empty:
                returns = hist_data['Close'].pct_change().dropna()
                volatility = returns.std() * (252 ** 0.5)  # Annualized
            else:
                volatility = 0.3  # Default if no data
        except:
            volatility = 0.3  # Default volatility
        
        # Use Black-Scholes to estimate
        # Calculate d1 and d2
        time_to_expiration = days_to_expiration / 365.0
        risk_free_rate = 0.05  # Approximate 5% risk-free rate
        
        # Prevent division by zero
        if time_to_expiration < 0.01:
            time_to_expiration = 0.01
        
        d1 = (np.log(current_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiration) / (volatility * np.sqrt(time_to_expiration))
        d2 = d1 - volatility * np.sqrt(time_to_expiration)
        
        # Calculate price
        if option_type.lower() == 'call':
            price = current_price * norm.cdf(d1) - strike_price * np.exp(-risk_free_rate * time_to_expiration) * norm.cdf(d2)
        else:
            price = strike_price * np.exp(-risk_free_rate * time_to_expiration) * norm.cdf(-d2) - current_price * norm.cdf(-d1)
        
        # Ensure minimum price
        price = max(0.05, price)
        
        return price
    
    except Exception as e:
        print(f"Error getting option price: {str(e)}")
        # No fallback - we only want to provide real market data
        return {'error': 'Unable to retrieve accurate market data', 'data_available': False}

def calculate_option_at_stop_loss(current_stock_price, stop_loss_price, strike_price, current_option_price, 
                                 expiration_date, option_type, ticker_symbol=None):
    """
    Calculate what the option will be worth at the stop loss price level.
    This is more accurate than using the simplified Greeks approximation for stop-loss levels.
    
    Args:
        current_stock_price: Current stock price
        stop_loss_price: Stock price stop loss level
        strike_price: Option strike price
        current_option_price: Current market price of the option
        expiration_date: Option expiration date (string in format 'YYYY-MM-DD')
        option_type: 'call' or 'put'
        ticker_symbol: Stock ticker symbol (optional, used for looking up option data)
    
    Returns:
        Estimated option price at the stop loss level, along with an estimated percentage loss
    """
    try:
        # Convert dates to calculate days to expiration
        today = datetime.now().date()
        
        # Handle different expiration_date formats
        try:
            if isinstance(expiration_date, str):
                expiry = datetime.strptime(expiration_date, '%Y-%m-%d').date()
            elif hasattr(expiration_date, 'date'):
                expiry = expiration_date.date()
            else:
                # Assume it's already a date
                expiry = expiration_date
                
            days_to_expiration = max(1, (expiry - today).days)
        except Exception as e:
            print(f"Error calculating days to expiration in stop loss: {e}")
            days_to_expiration = 30  # Default to 30 days
        
        # Only attempt to use a ticker object if a valid ticker symbol is provided
        stock = None
        if ticker_symbol and isinstance(ticker_symbol, str) and not ticker_symbol.replace('.', '', 1).isdigit():
            # Only use the ticker if it looks like a valid symbol (not a number)
            stock = yf.Ticker(ticker_symbol)
            print(f"Using ticker: {ticker_symbol} for option calculations")
        
        # Get IV from current option chain
        try:
            chain = get_option_chain(stock, expiration_date, option_type)
            option_data = chain[chain['strike'] == strike_price]
            
            if not option_data.empty:
                iv = option_data['impliedVolatility'].iloc[0]
            else:
                # Cannot calculate without accurate IV data
                raise ValueError("Could not find option data for the specified strike price")
        except Exception as e:
            print(f"Error getting IV for option calculation: {e}")
            # Cannot calculate without accurate market data
            raise ValueError("Could not retrieve implied volatility data")
        
        # Get Greeks for more accurate estimation
        greeks = get_option_greeks(stock, expiration_date, strike_price, option_type)
        
        # If Greeks are available, use them for a more accurate estimation
        if greeks:
            delta = greeks['delta']
            gamma = greeks['gamma']
            
            # Calculate price change due to stock price movement
            price_change = delta * (stop_loss_price - current_stock_price)
            
            # Add adjustment for convexity (gamma)
            gamma_adjustment = 0.5 * gamma * (stop_loss_price - current_stock_price) ** 2
            
            # Calculate option price at stop loss level
            option_price_at_stop = max(0, current_option_price + price_change + gamma_adjustment)
            
            # Ensure the price is at least the intrinsic value for very short-dated options
            if days_to_expiration <= 3:
                if option_type.lower() == 'call':
                    intrinsic_value = max(0, stop_loss_price - strike_price)
                else:
                    intrinsic_value = max(0, strike_price - stop_loss_price)
                option_price_at_stop = max(option_price_at_stop, intrinsic_value)
        else:
            # If Greeks aren't available, we can't calculate accurately
            print("Greeks data not available for option calculation")
            raise ValueError("Required Greeks data not available for accurate calculation")
        
        # Calculate percentage change
        percent_change = ((option_price_at_stop - current_option_price) / current_option_price) * 100
        
        return {
            "price": option_price_at_stop,
            "percent_change": percent_change
        }
    except Exception as e:
        print(f"Error calculating option price at stop loss: {str(e)}")
        # Don't provide synthetic data if accurate data is unavailable
        return {
            "error": "Unable to calculate option price at stop loss level with current market data",
            "data_available": False
        }

def calculate_theta_decay(current_option_price, theta, days_ahead=1, hours_ahead=12):
    """
    Calculate the expected theta decay impact on an option over a specified time period.
    
    Args:
        current_option_price: Current market price of the option
        theta: Option's theta value (daily decay)
        days_ahead: Number of days to project theta decay
        hours_ahead: Additional hours to add to the projection
        
    Returns:
        Dictionary with theta decay information
    """
    try:
        # Calculate the time fraction (days + hours/24)
        time_fraction = days_ahead + (hours_ahead / 24.0)
        
        # Calculate the expected theta decay amount
        theta_decay_amount = theta * time_fraction
        
        # Theta is typically negative, so we're ensuring it's treated as a decay
        # If theta is positive (unusual), treat it as negative for decay calculation
        decay_value = theta_decay_amount if theta_decay_amount < 0 else -abs(theta_decay_amount)
        
        # Calculate new projected price
        projected_price = current_option_price + decay_value
        
        # Ensure price doesn't go negative
        projected_price = max(0, projected_price)
        
        # Calculate percent change
        percent_change = ((projected_price - current_option_price) / current_option_price) * 100
        
        # Generate a warning status if theta decay is significant (> 5%)
        warning_status = False
        warning_message = ""
        
        # Theta is typically negative, so we're looking at the magnitude of the percent change
        if abs(percent_change) > 5:
            warning_status = True
            warning_message = (
                f"⚠️ **THETA DECAY WARNING** ⚠️\n"
                f"Your option may lose approximately ${abs(theta_decay_amount):.2f} (about {abs(percent_change):.1f}%) "
                f"in value over the next {days_ahead} day(s) and {hours_ahead} hour(s) due to time decay alone.\n"
                f"Projected option price: ${projected_price:.2f}\n"
                f"Consider adjusting your position if you're holding short-term options."
            )
            
        return {
            "original_price": current_option_price,
            "projected_price": projected_price,
            "theta_decay_amount": theta_decay_amount,
            "percent_change": percent_change,
            "warning_status": warning_status,
            "warning_message": warning_message
        }
        
    except Exception as e:
        print(f"Error calculating theta decay: {str(e)}")
        return {
            "error": "Unable to calculate theta decay with current market data",
            "data_available": False
        }
        
def calculate_expiry_theta_decay(current_option_price, theta, expiration_date, max_days=7, interval=1):
    """
    Calculate theta decay projections until the expiration date with configurable intervals.
    
    Args:
        current_option_price: Current market price of the option
        theta: Option's theta value (daily decay)
        expiration_date: Option expiration date (string in format 'YYYY-MM-DD')
        max_days: Maximum number of days to project (to avoid very long messages)
        interval: Interval between projections in days (1=daily, 7=weekly, etc.)
        
    Returns:
        Dictionary with detailed theta decay information
    """
    try:
        # Parse the expiration date
        today = datetime.now().date()
        
        try:
            if isinstance(expiration_date, str):
                expiry = datetime.strptime(expiration_date, '%Y-%m-%d').date()
            elif hasattr(expiration_date, 'date'):
                expiry = expiration_date.date()
            else:
                # Assume it's already a date
                expiry = expiration_date
                
            # Calculate days to expiration
            days_to_expiry = max(0, (expiry - today).days)
        except Exception as e:
            print(f"Error calculating days to expiry in theta decay calculation: {e}")
            # Instead of using default values, raise an error to avoid synthetic data
            raise ValueError(f"Unable to parse expiration date: {expiration_date}")
        
        # If expiration is in the past or today, return a warning
        if days_to_expiry <= 0:
            return {
                "original_price": current_option_price,
                "interval_decay": [],
                "warning_status": True,
                "warning_message": f"⚠️ **THETA DECAY WARNING** ⚠️\nThis option expires today or has already expired ({expiration_date})."
            }
        
        # Get interval description text
        interval_text = "day" if interval == 1 else f"{interval}-day" if interval < 7 else "week" if interval == 7 else f"{interval}-day"
        
        # Calculate the maximum number of intervals to display
        max_intervals = max(1, max_days // interval)
        projection_intervals = min(days_to_expiry // interval + (1 if days_to_expiry % interval > 0 else 0), max_intervals)
        
        # Calculate decay at each interval
        interval_decay = []
        running_price = current_option_price
        significant_decay = False
        
        for i in range(1, projection_intervals + 1):
            current_day = i * interval
            current_day = min(current_day, days_to_expiry)  # Ensure we don't go beyond expiry
            
            # Calculate price after this interval's decay
            # Theta is typically negative, so we're ensuring it's treated as a decay
            decay_amount_per_day = theta * 1.0  # Daily decay
            # If theta is positive (unusual), treat it as negative for decay calculation
            decay_value_per_day = decay_amount_per_day if decay_amount_per_day < 0 else -abs(decay_amount_per_day)
            
            # Total decay for this interval
            interval_days = interval if i * interval <= days_to_expiry else days_to_expiry - ((i-1) * interval)
            total_decay_for_interval = decay_value_per_day * interval_days
            
            new_price = running_price + total_decay_for_interval
            new_price = max(0, new_price)  # Ensure price doesn't go negative
            
            # Calculate percent change from previous interval
            interval_percent = ((new_price - running_price) / running_price) * 100
            
            # Calculate cumulative percent change from original price
            cumulative_percent = ((new_price - current_option_price) / current_option_price) * 100
            
            # Store the interval's decay information
            interval_decay.append({
                "interval": i,
                "days": current_day,
                "date": (today + timedelta(days=current_day)).strftime('%Y-%m-%d'),
                "price": new_price,
                "decay_amount": total_decay_for_interval,
                "interval_percent": interval_percent,
                "cumulative_percent": cumulative_percent
            })
            
            # Update running price for next iteration
            running_price = new_price
            
            # Check if decay has become significant
            if abs(cumulative_percent) > 5:
                significant_decay = True
        
        # Generate warning message with interval breakdown
        warning_status = significant_decay
        warning_message = ""
        
        if warning_status:
            # Create the header for the warning message
            warning_message = ""
            
            # Use appropriate description based on interval
            if interval == 1:
                warning_message += f"Your option is projected to decay over the next {projection_intervals} days:\n\n"
            elif interval == 7:
                warning_message += f"Your option is projected to decay over the next {projection_intervals} weeks:\n\n"
            else:
                warning_message += f"Your option is projected to decay over the next {projection_intervals} {interval_text} intervals:\n\n"
            
            # Add interval breakdown
            for info in interval_decay:
                if interval == 1:
                    warning_message += (
                        f"**Day {info['interval']} ({info['date']}):** "
                        f"${info['price']:.2f} ({info['interval_percent']:.1f}% daily, {info['cumulative_percent']:.1f}% total)\n"
                    )
                elif interval == 7:
                    warning_message += (
                        f"**Week {info['interval']} ({info['date']}):** "
                        f"${info['price']:.2f} ({info['interval_percent']:.1f}% weekly, {info['cumulative_percent']:.1f}% total)\n"
                    )
                else:
                    warning_message += (
                        f"**{interval_text} {info['interval']} ({info['date']}):** "
                        f"${info['price']:.2f} ({info['interval_percent']:.1f}% for period, {info['cumulative_percent']:.1f}% total)\n"
                    )
            
            # Add advice
            if days_to_expiry <= 7:
                warning_message += f"\n⚠️ **Critical Warning:** This option is in its final week before expiration when theta decay accelerates dramatically."
            elif days_to_expiry <= 30:
                warning_message += f"\n⚠️ **Warning:** Options typically experience accelerated decay in their final month."
            
            warning_message += f"\nConsider your exit strategy carefully as time decay becomes more significant near expiration."
        
        return {
            "original_price": current_option_price,
            "daily_decay": interval_decay,  # Changed from daily_decay to interval_decay
            "interval_decay": interval_decay, 
            "days_to_expiry": days_to_expiry,
            "warning_status": warning_status,
            "warning_message": warning_message
        }
        
    except Exception as e:
        print(f"Error calculating expiry theta decay: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            "error": "Unable to calculate theta decay projections with current market data",
            "data_available": False
        }