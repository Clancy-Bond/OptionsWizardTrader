import re
import os
import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# List of common market indices and popular stocks to pre-validate
COMMON_INDICES = [
    # Major indices
    'SPX', 'VIX', 'DJI', 'IXIC', 'RUT', 'NDX', 'FTSE', 'GDAXI', 'HSI', 'N225',
    
    # ETFs for indices
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'XLF', 'XLE', 'XLK', 'XLI', 'XLV', 'XLP',
    'XLU', 'XLB', 'XLY', 'GLD', 'SLV', 'USO', 'UNG', 'TLT', 'VXX', 'UVXY', 'SVXY',
    
    # Major tech stocks
    'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE',
    'INTC', 'CSCO', 'ORCL', 'IBM', 'CRM', 'AMD', 'AMAT', 'AVGO', 'QCOM', 'ACN',
    
    # Other major stocks
    'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'V', 'MA', 'PFE', 'JNJ', 'MRK', 'ABBV',
    'WMT', 'TGT', 'HD', 'LOW', 'KO', 'PEP', 'MCD', 'SBUX', 'DIS', 'CMCSA', 'T', 'VZ',
    'PG', 'CL', 'NKE', 'F', 'GM', 'GE', 'BA', 'CAT', 'MMM', 'XOM', 'CVX', 'COP'
]

# Cache of validated tickers for performance
VALIDATED_TICKERS = set(COMMON_INDICES)

# Common English words and query terms to exclude (actually extensive list)
COMMON_WORDS = [
    # Basic query words
    'WHAT', 'WILL', 'THE', 'FOR', 'ARE', 'OPTIONS', 'OPTION', 'CALLS', 'PUTS',
    'CALL', 'PUT', 'SHOW', 'GET', 'WHO', 'WHY', 'HOW', 'WHEN', 'UNUSUAL', 'ACTIVITY',
    
    # Articles and prepositions
    'THE', 'AN', 'AND', 'BUT', 'OR', 'SO', 'TO', 'FROM', 'AT', 'BY', 'IN', 'OF', 'ON', 'OUT',
    'INTO', 'ONTO', 'UPON', 'WITHIN', 'WITHOUT', 'THROUGH', 'THROUGHOUT', 'ACROSS', 'ALONG',
    'AROUND', 'OVER', 'UNDER', 'ABOVE', 'BELOW', 'BEFORE', 'AFTER', 'DURING', 'SINCE', 'UNTIL',
    'BETWEEN', 'AMONG', 'AGAINST', 'BESIDE', 'BESIDES', 'OFF', 'ABOUT', 'BEYOND', 'NEAR',
    'WITH', 'TOWARD', 'TOWARDS', 'DESPITE', 'PER', 'VERSUS', 'VIA', 'AMID', 'AMIDST',
    
    # Pronouns
    'THIS', 'THAT', 'THESE', 'THOSE', 'THEY', 'THEM', 'THEIR', 'THEIRS', 'THEMSELVES',
    'YOU', 'YOUR', 'YOURS', 'YOURSELF', 'YOURSELVES', 'HE', 'HIM', 'HIS', 'HIMSELF',
    'SHE', 'HER', 'HERS', 'HERSELF', 'IT', 'ITS', 'ITSELF', 'WE', 'US', 'OUR', 'OURS',
    'OURSELVES', 'WHO', 'WHOM', 'WHOSE', 'WHICH', 'WHAT', 'WHATEVER', 'WHICHEVER',
    'WHOEVER', 'WHOMEVER', 'ANYONE', 'ANYTHING', 'ANYWHERE', 'SOMEONE', 'SOMETHING',
    'SOMEWHERE', 'EVERYONE', 'EVERYTHING', 'EVERYWHERE', 'NOBODY', 'NOTHING', 'NOWHERE',
    
    # Verbs
    'IS', 'ARE', 'AM', 'WAS', 'WERE', 'BE', 'BEEN', 'BEING', 'HAVE', 'HAS', 'HAD', 'HAVING',
    'DO', 'DOES', 'DID', 'DOING', 'WILL', 'WOULD', 'SHALL', 'SHOULD', 'CAN', 'COULD', 'MAY',
    'MIGHT', 'MUST', 'GOING', 'WANT', 'WANTS', 'WANTED', 'WANTING', 'NEED', 'NEEDS', 'NEEDED',
    'MAKE', 'MAKES', 'MADE', 'MAKING', 'TAKE', 'TAKES', 'TOOK', 'TAKEN', 'TAKING', 'GIVE',
    'GIVES', 'GAVE', 'GIVEN', 'GIVING', 'FIND', 'FINDS', 'FOUND', 'FINDING', 'THINK', 'THINKS',
    'THOUGHT', 'THINKING', 'KNOW', 'KNOWS', 'KNEW', 'KNOWN', 'KNOWING', 'SEE', 'SEES', 'SAW',
    'SEEN', 'SEEING', 'LOOK', 'LOOKS', 'LOOKED', 'LOOKING', 'COME', 'COMES', 'CAME', 'COMING',
    'GET', 'GETS', 'GOT', 'GOTTEN', 'GETTING', 'HELP', 'HELPS', 'HELPED', 'HELPING',
    
    # Adjectives and adverbs
    'GOOD', 'BETTER', 'BEST', 'BAD', 'WORSE', 'WORST', 'HIGH', 'HIGHER', 'HIGHEST', 'LOW',
    'LOWER', 'LOWEST', 'BIG', 'BIGGER', 'BIGGEST', 'SMALL', 'SMALLER', 'SMALLEST', 'MANY',
    'MORE', 'MOST', 'FEW', 'FEWER', 'FEWEST', 'MUCH', 'SOME', 'ANY', 'ALL', 'EACH', 'EVERY',
    'SEVERAL', 'BOTH', 'EITHER', 'NEITHER', 'FAST', 'FASTER', 'FASTEST', 'SLOW', 'SLOWER',
    'SLOWEST', 'EARLY', 'EARLIER', 'EARLIEST', 'LATE', 'LATER', 'LATEST', 'NOW', 'THEN',
    'SOON', 'ALWAYS', 'NEVER', 'SOMETIMES', 'OFTEN', 'RARELY', 'USUALLY', 'VERY', 'QUITE',
    'RATHER', 'SOMEWHAT', 'TOO', 'ENOUGH', 'JUST', 'ONLY', 'ALSO', 'ELSE', 'EVEN',
    
    # Trading and financial terms
    'PRICE', 'VALUE', 'TARGET', 'WORTH', 'ESTIMATE', 'TICKER', 'STOCK', 'SYMBOL', 'DATA',
    'INFO', 'CHECK', 'LIST', 'FLOW', 'WHALE', 'VOLUME', 'TRADING', 'MARKET', 'BUY', 'SELL',
    'LONG', 'SHORT', 'HOLD', 'TRADE', 'TRADES', 'TRADING', 'POSITION', 'POSITIONS', 'PLAY',
    'PLAYS', 'MOVE', 'MOVES', 'MOVING', 'UPSIDE', 'DOWNSIDE', 'BULL', 'BEAR', 'BULLISH',
    'BEARISH', 'NEUTRAL', 'VOLATILITY', 'PREMIUM', 'DISCOUNT', 'RISK', 'REWARD', 'HEDGE',
    'HEDGING', 'SPREAD', 'SPREADS', 'STRATEGY', 'STRATEGIES', 'CHART', 'CHARTS',
    
    # Quantities and dates
    'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH', 'LAST', 'NEXT', 'PREVIOUS', 'TODAY',
    'TOMORROW', 'YESTERDAY', 'WEEK', 'MONTH', 'YEAR', 'DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY',
    'QUARTERLY', 'DAY', 'NIGHT', 'MORNING', 'EVENING', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL',
    'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER', 'MONDAY',
    'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY',
    
    # Polite conversation words
    'PLEASE', 'THANKS', 'THANK', 'SORRY', 'EXCUSE', 'HELLO', 'HI', 'BYE', 'GOODBYE', 'WELCOME'
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

import polygon_integration as polygon

def fetch_all_tickers():
    """
    Fetch a comprehensive list of all stock tickers from major exchanges.
    This function will use Polygon.io API to fetch tickers.
    
    Returns:
        A set of valid ticker symbols
    """
    # Try to use Polygon API first (much more comprehensive)
    try:
        # Check if we have a Polygon API key
        if os.getenv('POLYGON_API_KEY'):
            print("Using Polygon.io API to fetch comprehensive ticker list...")
            polygon_tickers = polygon.fetch_all_tickers()
            if polygon_tickers and len(polygon_tickers) > 100:
                print(f"Successfully fetched {len(polygon_tickers)} tickers from Polygon.io")
                # Update our cache
                VALIDATED_TICKERS.update(polygon_tickers)
                return polygon_tickers
    except Exception as e:
        print(f"Error using Polygon API: {str(e)}")
    
    # Fall back to our original method if Polygon fails
    print("Falling back to Yahoo Finance method for tickers...")
    all_tickers = set(COMMON_INDICES)  # Start with our predefined list
    
    try:
        # Method 1: Using yfinance directly to get popular symbols
        popular_tickers = [
            # Major tech stocks
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'AMZN', 'TSLA', 'NVDA', 'AMD', 'INTC',
            'IBM', 'ORCL', 'CRM', 'CSCO', 'ADBE', 'NFLX', 'PYPL', 'QCOM', 'TXN', 'AVGO',
            
            # Financial stocks
            'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'AXP', 'V', 'MA', 'BLK',
            'BRK.A', 'BRK.B', 'PNC', 'USB', 'TFC', 'COF', 'AIG', 'MET', 'PRU',
            
            # Consumer stocks
            'AAPL', 'AMZN', 'WMT', 'TGT', 'HD', 'LOW', 'MCD', 'SBUX', 'NKE', 'DIS',
            'KO', 'PEP', 'PG', 'JNJ', 'PFE', 'MRK', 'CVS', 'UNH', 'T', 'VZ', 
            
            # Energy and industrial stocks
            'XOM', 'CVX', 'BP', 'COP', 'EOG', 'SLB', 'GE', 'BA', 'CAT', 'MMM', 
            'HON', 'UPS', 'FDX', 'RTX', 'LMT', 'GM', 'F', 'TSLA'
        ]
        all_tickers.update(popular_tickers)
        print(f"Added {len(popular_tickers)} popular tickers directly")
        
        # Method 2: Use indexes to get their components
        major_indices = ['SPY', 'QQQ', 'DIA', 'IWM']
        for index in major_indices:
            try:
                # Get historical data for this index to verify it exists
                index_ticker = yf.Ticker(index)
                hist = index_ticker.history(period="1d")
                
                if not hist.empty:
                    print(f"Successfully validated index: {index}")
                    # For each validated index, add its components (if we could)
                    # This is a placeholder as yfinance doesn't easily provide components
            except Exception as e:
                print(f"Error validating index {index}: {str(e)}")
        
        # Method 3: Generate common pattern tickers (1-4 letters)
        import string
        # Generate single letter tickers (e.g., F, X)
        for letter in string.ascii_uppercase:
            potential_ticker = letter
            try:
                ticker = yf.Ticker(potential_ticker)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    all_tickers.add(potential_ticker)
                    print(f"Added single-letter ticker: {potential_ticker}")
            except:
                pass
                
        # Method 4: Add tickers from most active lists
        # We can't easily scrape these, but we can add known active tickers
        active_tickers = [
            'SPY', 'QQQ', 'AAPL', 'TSLA', 'AMD', 'NVDA', 'BAC', 'F', 'PLTR', 'SOFI',
            'NIO', 'LCID', 'INTC', 'CCL', 'T', 'SNAP', 'PLUG', 'PFE', 'AAL', 'VALE',
            'AMZN', 'MSFT', 'META', 'GOOGL', 'BABA', 'AMC', 'GME', 'BB', 'NOK', 'WISH',
            'TLRY', 'COIN', 'RIVN', 'HOOD', 'RBLX', 'DKNG', 'SPCE', 'OPEN', 'AFRM'
        ]
        all_tickers.update(active_tickers)
        print(f"Added {len(active_tickers)} active tickers")
        
        # Save the combined ticker list to a local file for backup
        try:
            with open('valid_tickers.json', 'w') as f:
                json.dump(list(all_tickers), f)
            print(f"Saved {len(all_tickers)} tickers to valid_tickers.json")
        except Exception as e:
            print(f"Error saving tickers to file: {str(e)}")
            
    except Exception as e:
        print(f"Error during ticker fetching: {str(e)}")
        
    # Try to load from local file if available or if we have few tickers
    if len(all_tickers) < 100:
        try:
            if os.path.exists('valid_tickers.json'):
                with open('valid_tickers.json', 'r') as f:
                    loaded_tickers = json.load(f)
                    all_tickers.update(loaded_tickers)
                print(f"Loaded {len(loaded_tickers)} tickers from local backup file")
        except Exception as backup_error:
            print(f"Error loading backup ticker list: {str(backup_error)}")
    
    # Generate and add 'synthetic' tickers of common patterns if our list is still small
    if len(all_tickers) < 200:
        print("Adding synthetic tickers of common patterns...")
        # Add two-letter tickers from common exchanges
        two_letter_prefixes = ['AA', 'AB', 'AC', 'BA', 'BB', 'BC', 'CA', 'CB', 'CC']
        all_tickers.update(two_letter_prefixes)
        
        # Add common three-letter patterns
        common_three = [
            'AAA', 'AAB', 'AAC', 'ABA', 'ABB', 'ABC', 'BAA', 'BAB', 'BAC',
            'BBA', 'BBB', 'BBC', 'CAA', 'CAB', 'CAC', 'CBA', 'CBB', 'CBC'
        ]
        all_tickers.update(common_three)
        
        print(f"Added synthetic patterns to reach {len(all_tickers)} tickers")
    
    return all_tickers

def is_valid_ticker(ticker):
    """
    Check if a symbol is a valid stock ticker by checking against our cached list
    or using Polygon.io API with Yahoo Finance as backup.
    
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
    
    # Try Polygon.io API first if available
    if os.getenv('POLYGON_API_KEY'):
        try:
            if polygon.is_valid_ticker(ticker):
                # It's a valid ticker - add to cache
                VALIDATED_TICKERS.add(ticker)
                print(f"Polygon validated and cached ticker: {ticker}")
                return True
        except Exception as e:
            print(f"Error with Polygon validation for {ticker}: {str(e)}")
    
    # Fall back to Yahoo Finance if Polygon fails or isn't available
    try:
        # Try a quick info lookup for a known field (faster than full info)
        # Just check if we can get price data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        
        if not hist.empty:
            # It's a valid ticker - add to cache
            VALIDATED_TICKERS.add(ticker)
            print(f"Yahoo validated and cached ticker: {ticker}")
            return True
        return False
    except Exception as e:
        print(f"Error validating ticker {ticker} with Yahoo: {str(e)}")
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