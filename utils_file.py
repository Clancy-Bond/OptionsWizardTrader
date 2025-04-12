import re
import os
import json
import yfinance as yf
from datetime import datetime, timedelta

# List of common market indices that might be mistaken for tickers
COMMON_INDICES = ['SPX', 'VIX', 'DJI', 'IXIC', 'RUT', 'NDX', 'SPY', 'QQQ', 'IWM', 'MSFT', 'AAPL', 'GOOGL', 'AMZN', 'TSLA']

# Cache of validated tickers for performance
VALIDATED_TICKERS = set(COMMON_INDICES)

# Common English words and query terms to exclude (extensive list)
COMMON_WORDS = [
    'WHAT', 'WILL', 'THE', 'FOR', 'ARE', 'OPTIONS', 'OPTION', 'CALLS', 'PUTS',
    'CALL', 'PUT', 'SHOW', 'GET', 'WHO', 'WHY', 'HOW', 'WHEN', 'UNUSUAL', 'ACTIVITY',
    'THIS', 'THAT', 'HERE', 'THERE', 'FROM', 'INTO', 'YOUR', 'WITH', 'MORE', 'LESS',
    'SOME', 'MANY', 'MUCH', 'MOST', 'EACH', 'EVERY', 'BOTH', 'THAN', 'THEN', 'THEY',
    'THEM', 'THEIR', 'OTHER', 'ANOTHER', 'WOULD', 'COULD', 'SHOULD', 'ABOUT', 'THESE',
    'THOSE', 'WHICH', 'WHERE', 'WHEN', 'WHILE', 'AFTER', 'BEFORE', 'DURING', 'UNDER',
    'OVER', 'ABOVE', 'BELOW', 'BETWEEN', 'AMONG', 'AGAINST', 'WITHOUT', 'WITHIN',
    'THROUGH', 'THROUGHOUT', 'ACROSS', 'ALONG', 'AROUND', 'UPON', 'NEXT', 'LAST',
    'FIRST', 'SECOND', 'THIRD', 'LIKE', 'WANT', 'HAVE', 'NEED', 'FIND', 'LOOK',
    'MAKE', 'HELP', 'GIVE', 'TAKE', 'KNOW', 'COME', 'PRICE', 'VALUE', 'TARGET',
    'WORTH', 'ESTIMATE', 'TICKER', 'STOCK', 'SYMBOL', 'DATA', 'INFO', 'CHECK',
    'LIST', 'PLEASE', 'THANKS', 'FLOW', 'WHALE', 'VOLUME', 'TRADING', 'MARKET',
    'GOOD', 'BAD', 'HIGH', 'LOW', 'BEST', 'WORST', 'JUST', 'VERY', 'ONLY'
]

def format_ticker(ticker):
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
    ticker = re.sub(r'[^A-Z0-9\.]', '', ticker)
    
    # Check if it's a valid ticker format
    if not ticker or len(ticker) > 10:
        return 'AAPL'  # Default to AAPL if invalid
    
    return ticker

def validate_inputs(ticker, target_price=None):
    """
    Validate user inputs.
    
    Args:
        ticker: Stock ticker symbol
        target_price: Target stock price (optional)
    
    Returns:
        Error message if validation fails, None otherwise
    """
    if not ticker or len(ticker) > 10:
        return "Please enter a valid ticker symbol."
    
    if target_price is not None and target_price <= 0:
        return "Target price must be greater than zero."
    
    return None

def parse_relative_date(date_text):
    """
    Parse relative date references like 'next Friday', 'tomorrow', etc.
    
    Args:
        date_text: Text containing relative date reference
    
    Returns:
        Date in YYYY-MM-DD format or None if parsing fails
    """
    date_text = date_text.lower()
    today = datetime.now().date()
    
    if 'tomorrow' in date_text:
        target_date = today + timedelta(days=1)
        return target_date.strftime('%Y-%m-%d')
    
    if 'today' in date_text:
        return today.strftime('%Y-%m-%d')
        
    if 'next week' in date_text:
        target_date = today + timedelta(days=7)
        return target_date.strftime('%Y-%m-%d')
        
    if 'next month' in date_text:
        # Approximate a month as 30 days
        target_date = today + timedelta(days=30)
        return target_date.strftime('%Y-%m-%d')
        
    # Check for days of the week
    days = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day, day_num in days.items():
        if day in date_text:
            # Calculate days until the next occurrence of this day
            current_day_num = today.weekday()
            days_ahead = (day_num - current_day_num) % 7
            
            # If "next" is specified and it's the same day of the week, add a week
            if 'next' in date_text and days_ahead == 0:
                days_ahead = 7
            
            # If it's the same day but without "next", use today's date
            if days_ahead == 0 and 'next' not in date_text:
                return today.strftime('%Y-%m-%d')
                
            # Calculate the target date
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime('%Y-%m-%d')
    
    return None

def is_valid_ticker(ticker):
    """
    Check if a symbol is a valid stock ticker by checking with Yahoo Finance.
    
    Args:
        ticker: The symbol to check
        
    Returns:
        Boolean indicating if it's a valid ticker
    """
    if not ticker or not isinstance(ticker, str):
        return False
        
    # Convert to uppercase and remove any leading $ sign
    ticker = ticker.upper()
    if ticker.startswith('$'):
        ticker = ticker[1:]
    
    # Basic format validation: 1-5 characters, all uppercase letters
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        return False
        
    # Quick check in cache to avoid API calls
    if ticker in VALIDATED_TICKERS:
        return True
    
    # Quick check against common words
    if ticker in COMMON_WORDS:
        return False
    
    try:
        # Try a quick info lookup for a known field (faster than full info)
        # Just check if we can get price data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        
        if not hist.empty:
            # It's a valid ticker - add to cache
            VALIDATED_TICKERS.add(ticker)
            print(f"Validated and cached ticker: {ticker}")
            return True
        return False
    except Exception as e:
        print(f"Error validating ticker {ticker}: {str(e)}")
        return False

def load_permissions():
    """
    Load bot permissions from JSON file
    
    Returns:
        Dictionary of permissions
    """
    permissions = {}
    try:
        if os.path.exists("discord_permissions.json"):
            with open("discord_permissions.json", "r") as f:
                permissions = json.load(f)
    except Exception as e:
        print(f"Error loading permissions: {str(e)}")
    
    return permissions