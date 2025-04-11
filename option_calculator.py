import yfinance as yf
import numpy as np
import datetime
from calculate_dynamic_theta_decay import project_theta_decay

def calculate_option_price(ticker, strike, expiry, option_type):
    """
    Calculate option price and Greeks using Black-Scholes model
    
    Args:
        ticker (str): The ticker symbol
        strike (float): The strike price
        expiry (str): The expiration date
        option_type (str): 'call' or 'put'
    
    Returns:
        dict: Option price and Greeks
    """
    # Get current stock data
    stock = yf.Ticker(ticker)
    try:
        S = stock.info['regularMarketPrice']  # Current stock price
    except:
        # Fallback to last close if real-time data unavailable
        data = yf.download(ticker, period='1d', progress=False)
        S = data['Close'].iloc[-1]
    
    # Parse expiration date
    if expiry:
        try:
            # Try common date formats
            try:
                exp_date = datetime.datetime.strptime(expiry, '%m/%d/%Y').date()
            except ValueError:
                try:
                    exp_date = datetime.datetime.strptime(expiry, '%m-%d-%Y').date()
                except ValueError:
                    exp_date = datetime.datetime.strptime(expiry, '%d %b %Y').date()
        except:
            # Default to 30 days if parsing fails
            exp_date = datetime.date.today() + datetime.timedelta(days=30)
    else:
        # Default to 30 days if no expiry provided
        exp_date = datetime.date.today() + datetime.timedelta(days=30)
    
    # Calculate time to expiration in years
    today = datetime.date.today()
    T = (exp_date - today).days / 365.0
    T = max(0.01, T)  # Minimum to avoid division by zero
    
    # If strike is None, use ATM strike
    K = strike if strike is not None else S
    
    # Constants for Black-Scholes
    r = 0.05  # Risk-free rate (approximate)
    
    # Calculate historical volatility
    hist_data = yf.download(ticker, period='3mo', progress=False)
    returns = np.log(hist_data['Close'] / hist_data['Close'].shift(1))
    sigma = returns.std() * np.sqrt(252)  # Annualized volatility
    
    # Black-Scholes formula
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate option price
    if option_type.lower() == 'call':
        price = S * norm_cdf(d1) - K * np.exp(-r * T) * norm_cdf(d2)
    else:  # put
        price = K * np.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    
    # Calculate Greeks
    delta = calculate_delta(d1, option_type)
    gamma = calculate_gamma(d1, S, sigma, T)
    theta = calculate_theta(d1, d2, S, K, r, sigma, T, option_type)
    vega = calculate_vega(d1, S, T, sigma)
    rho = calculate_rho(d2, K, T, r, option_type)
    
    # Project theta decay
    dte = (exp_date - today).days
    theta_decay = project_theta_decay(price, theta, dte)
    
    return {
        'price': price,
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'rho': rho,
        'theta_decay': theta_decay,
        'implied_volatility': sigma,
        'days_to_expiration': dte
    }

def norm_cdf(x):
    """Calculate the cumulative distribution function of the normal distribution"""
    return (1.0 + np.math.erf(x / np.sqrt(2.0))) / 2.0

def calculate_delta(d1, option_type):
    """Calculate Delta greek"""
    if option_type.lower() == 'call':
        return norm_cdf(d1)
    else:  # put
        return norm_cdf(d1) - 1

def calculate_gamma(d1, S, sigma, T):
    """Calculate Gamma greek"""
    return norm_pdf(d1) / (S * sigma * np.sqrt(T))

def calculate_theta(d1, d2, S, K, r, sigma, T, option_type):
    """Calculate Theta greek"""
    term1 = -S * norm_pdf(d1) * sigma / (2 * np.sqrt(T))
    
    if option_type.lower() == 'call':
        term2 = -r * K * np.exp(-r * T) * norm_cdf(d2)
        return (term1 + term2) / 365  # Convert to daily theta
    else:  # put
        term2 = r * K * np.exp(-r * T) * norm_cdf(-d2)
        return (term1 + term2) / 365  # Convert to daily theta

def calculate_vega(d1, S, T, sigma):
    """Calculate Vega greek"""
    return S * np.sqrt(T) * norm_pdf(d1) / 100  # Vega is typically expressed per 1% change

def calculate_rho(d2, K, T, r, option_type):
    """Calculate Rho greek"""
    if option_type.lower() == 'call':
        return K * T * np.exp(-r * T) * norm_cdf(d2) / 100
    else:  # put
        return -K * T * np.exp(-r * T) * norm_cdf(-d2) / 100

def norm_pdf(x):
    """Calculate the probability density function of the normal distribution"""
    return np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
