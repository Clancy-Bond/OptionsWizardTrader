"""
Polygon.io API integration for OptionsWizard
This module provides functions to interact with Polygon.io's APIs
for stock and options data retrieval.
"""
import os
import requests
import json
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

# Cache for ticker validity to minimize API calls
valid_ticker_cache = set()
exchange_ticker_cache = {}
option_chain_cache = {}

def get_headers():
    """
    Get authenticated headers for Polygon API requests
    """
    return {
        'Authorization': f'Bearer {POLYGON_API_KEY}'
    }

def fetch_all_tickers():
    """
    Fetch a comprehensive list of all stock tickers from Polygon.io
    This function gets all active tickers across major exchanges
    
    Returns:
        A set of valid ticker symbols
    """
    print("Fetching comprehensive ticker list from Polygon.io...")
    all_tickers = set()
    
    try:
        # Endpoint for ticker types
        types = ['CS', 'ETF']  # Common Stock and ETFs
        for ticker_type in types:
            endpoint = f"{BASE_URL}/v3/reference/tickers?type={ticker_type}&active=true&limit=1000"
            
            # Make initial request
            response = requests.get(endpoint, headers=get_headers())
            if response.status_code != 200:
                print(f"Error fetching tickers: {response.status_code} - {response.text}")
                continue
            
            data = response.json()
            
            # Add tickers from first page
            results = data.get('results', [])
            for item in results:
                ticker = item.get('ticker')
                if ticker:
                    all_tickers.add(ticker)
            
            # Paginate through remaining results if more pages exist
            next_url = data.get('next_url')
            page_count = 1
            
            while next_url and page_count < 5:  # Limit to 5 pages to avoid excessive API usage
                full_url = f"{next_url}&apiKey={POLYGON_API_KEY}"
                response = requests.get(full_url)
                
                if response.status_code != 200:
                    print(f"Error fetching page {page_count+1}: {response.status_code}")
                    break
                
                data = response.json()
                results = data.get('results', [])
                for item in results:
                    ticker = item.get('ticker')
                    if ticker:
                        all_tickers.add(ticker)
                
                next_url = data.get('next_url')
                page_count += 1
                print(f"Processed page {page_count} - Total tickers: {len(all_tickers)}")
        
        # Save to cache file for future use
        try:
            with open('polygon_tickers.json', 'w') as f:
                json.dump(list(all_tickers), f)
            print(f"Saved {len(all_tickers)} tickers to polygon_tickers.json")
        except Exception as e:
            print(f"Error saving tickers: {str(e)}")
            
    except Exception as e:
        print(f"Error during Polygon ticker fetching: {str(e)}")
        
        # Try to load from backup file
        try:
            if os.path.exists('polygon_tickers.json'):
                with open('polygon_tickers.json', 'r') as f:
                    cached_tickers = json.load(f)
                all_tickers.update(cached_tickers)
                print(f"Loaded {len(cached_tickers)} tickers from backup file")
        except Exception as backup_error:
            print(f"Error loading backup ticker list: {str(backup_error)}")
    
    # Update the in-memory cache
    valid_ticker_cache.update(all_tickers)
    
    return all_tickers

def is_valid_ticker(ticker):
    """
    Check if a symbol is a valid stock ticker using Polygon.io
    
    Args:
        ticker: The symbol to check
        
    Returns:
        Boolean indicating if it's a valid ticker
    """
    if not ticker:
        return False
    
    # Convert to uppercase
    ticker = ticker.upper()
    
    # Check in-memory cache first
    if ticker in valid_ticker_cache:
        return True
    
    # Make API call to validate ticker
    try:
        endpoint = f"{BASE_URL}/v3/reference/tickers?ticker={ticker}"
        response = requests.get(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error checking ticker {ticker}: {response.status_code}")
            return False
        
        data = response.json()
        results = data.get('results', [])
        
        if results and len(results) > 0:
            # Add to cache for future checks
            valid_ticker_cache.add(ticker)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error validating ticker {ticker}: {str(e)}")
        return False

def get_ticker_details(ticker):
    """
    Get detailed information about a ticker
    
    Args:
        ticker: The stock ticker symbol
        
    Returns:
        Dictionary with ticker details
    """
    if not ticker:
        return None
    
    ticker = ticker.upper()
    
    try:
        endpoint = f"{BASE_URL}/v3/reference/tickers/{ticker}"
        response = requests.get(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error fetching ticker details for {ticker}: {response.status_code}")
            return None
        
        data = response.json()
        result = data.get('results')
        
        if result:
            return result
        
        return None
        
    except Exception as e:
        print(f"Error fetching ticker details for {ticker}: {str(e)}")
        return None

def get_current_price(ticker):
    """
    Get the current market price for a ticker
    
    Args:
        ticker: The stock ticker symbol
        
    Returns:
        Current price or None if unavailable
    """
    if not ticker:
        return None
    
    ticker = ticker.upper()
    
    try:
        # Get latest trade
        endpoint = f"{BASE_URL}/v2/last/trade/{ticker}"
        response = requests.get(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error fetching current price for {ticker}: {response.status_code}")
            return None
        
        data = response.json()
        result = data.get('results')
        
        if result:
            return result.get('p')  # 'p' is the price field
        
        return None
        
    except Exception as e:
        print(f"Error fetching current price for {ticker}: {str(e)}")
        return None

def get_option_chain(ticker, expiration_date=None):
    """
    Get the option chain for a given stock and expiration date
    
    Args:
        ticker: The stock ticker symbol
        expiration_date: Optional date string in YYYY-MM-DD format
            If None, gets all available expiration dates
            
    Returns:
        Dictionary with option chain data
    """
    if not ticker:
        return None
    
    ticker = ticker.upper()
    
    # Check cache first if we have an expiration date
    cache_key = f"{ticker}_{expiration_date}"
    if expiration_date and cache_key in option_chain_cache:
        return option_chain_cache[cache_key]
    
    try:
        # Build the API endpoint
        if expiration_date:
            endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&expiration_date={expiration_date}"
        else:
            endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}"
        
        response = requests.get(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error fetching option chain for {ticker}: {response.status_code}")
            return None
        
        data = response.json()
        results = data.get('results', [])
        
        if expiration_date:
            # Cache the results for this expiration date
            option_chain_cache[cache_key] = results
        
        return results
        
    except Exception as e:
        print(f"Error fetching option chain for {ticker}: {str(e)}")
        return None

def get_option_expirations(ticker):
    """
    Get all available option expiration dates for a ticker
    
    Args:
        ticker: The stock ticker symbol
        
    Returns:
        List of expiration dates in YYYY-MM-DD format
    """
    if not ticker:
        return []
    
    ticker = ticker.upper()
    
    try:
        endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&limit=1000"
        response = requests.get(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error fetching option expirations for {ticker}: {response.status_code}")
            return []
        
        data = response.json()
        results = data.get('results', [])
        
        # Extract unique expiration dates
        expirations = set()
        for option in results:
            exp_date = option.get('expiration_date')
            if exp_date:
                expirations.add(exp_date)
        
        # Sort dates
        sorted_expirations = sorted(list(expirations))
        return sorted_expirations
        
    except Exception as e:
        print(f"Error fetching option expirations for {ticker}: {str(e)}")
        return []

def get_option_price(ticker, option_type, strike_price, expiration_date):
    """
    Get the current market price for an option
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        option_type: 'call' or 'put'
        strike_price: Option strike price
        expiration_date: Expiration date in YYYY-MM-DD format
        
    Returns:
        Current option price or None if unavailable
    """
    if not ticker or not option_type or not strike_price or not expiration_date:
        return None
    
    ticker = ticker.upper()
    option_type = option_type.lower()
    
    try:
        # First, get the option symbol
        chain = get_option_chain(ticker, expiration_date)
        
        if not chain:
            return None
        
        # Find the matching option
        option_symbol = None
        for option in chain:
            if (option.get('strike_price') == float(strike_price) and 
                option.get('contract_type').lower() == option_type):
                option_symbol = option.get('ticker')
                break
        
        if not option_symbol:
            print(f"Option not found: {ticker} {expiration_date} {strike_price} {option_type}")
            return None
        
        # Now get the latest price for this option
        endpoint = f"{BASE_URL}/v2/last/trade/{option_symbol}"
        response = requests.get(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error fetching option price: {response.status_code}")
            return None
        
        data = response.json()
        result = data.get('results')
        
        if result:
            return result.get('p')  # 'p' is the price field
        
        return None
        
    except Exception as e:
        print(f"Error fetching option price: {str(e)}")
        return None

def get_unusual_options_activity(ticker):
    """
    Get unusual options activity for a ticker based on volume spikes
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with unusual options activity data
    """
    if not ticker:
        return None
    
    ticker = ticker.upper()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Get options for today's date
        chain = get_option_chain(ticker)
        
        if not chain:
            return None
        
        # Get current stock price for context
        stock_price = get_current_price(ticker)
        
        # Track potential unusual activity
        unusual_activity = []
        
        # Look for unusual volume and premium patterns
        for option in chain:
            option_symbol = option.get('ticker')
            
            if not option_symbol:
                continue
                
            # Get option details
            strike = option.get('strike_price')
            expiry = option.get('expiration_date')
            contract_type = option.get('contract_type', '').lower()
            
            # Skip if missing key info
            if not strike or not expiry or not contract_type:
                continue
                
            # Check if near the money (within 10%)
            if stock_price and abs(strike - stock_price) / stock_price > 0.1:
                continue  # Skip deep OTM/ITM options
                
            # Get trades for this option
            endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=50&order=desc"
            response = requests.get(endpoint, headers=get_headers())
            
            if response.status_code != 200:
                continue
                
            data = response.json()
            trades = data.get('results', [])
            
            # Look for large size trades (>20 contracts)
            large_trades = [t for t in trades if t.get('size', 0) > 20]
            
            if large_trades:
                # Calculate some metrics
                total_volume = sum(t.get('size', 0) for t in large_trades)
                avg_price = sum(t.get('price', 0) * t.get('size', 0) for t in large_trades) / total_volume if total_volume > 0 else 0
                total_premium = total_volume * 100 * avg_price  # Each contract is 100 shares
                
                # Only include if premium is significant (>$10,000)
                if total_premium > 10000:
                    # Determine sentiment
                    sentiment = None
                    if contract_type == 'call':
                        sentiment = 'bullish'
                    elif contract_type == 'put':
                        sentiment = 'bearish'
                        
                    unusual_activity.append({
                        'contract': f"{ticker} {strike} {expiry} {contract_type.upper()}",
                        'volume': total_volume,
                        'avg_price': avg_price,
                        'premium': total_premium,
                        'sentiment': sentiment
                    })
        
        # Sort by premium in descending order
        unusual_activity.sort(key=lambda x: x['premium'], reverse=True)
        
        # Take top 5 (if we have that many)
        return unusual_activity[:5]
        
    except Exception as e:
        print(f"Error fetching unusual activity for {ticker}: {str(e)}")
        return None

def get_simplified_unusual_activity_summary(ticker):
    """
    Create a simplified, conversational summary of unusual options activity
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        A string with a conversational summary of unusual options activity
    """
    ticker = ticker.upper() if ticker else ""
    
    if not ticker:
        return "Please specify a valid ticker symbol."
    
    activity = get_unusual_options_activity(ticker)
    
    if not activity or len(activity) == 0:
        return f"📊 No significant unusual options activity detected for {ticker}.\n\nThis could indicate normal trading patterns or low options volume."
    
    # Determine overall sentiment
    bullish_count = sum(1 for item in activity if item.get('sentiment') == 'bullish')
    bearish_count = sum(1 for item in activity if item.get('sentiment') == 'bearish')
    
    if bullish_count > bearish_count:
        overall_sentiment = "bullish"
    elif bearish_count > bullish_count:
        overall_sentiment = "bearish"
    else:
        overall_sentiment = "neutral"
    
    # Create the summary
    summary = f"📊 {ticker} Unusual Options Activity: {overall_sentiment.upper()} BIAS\n\n"
    
    for i, item in enumerate(activity):
        contract = item.get('contract', '')
        volume = item.get('volume', 0)
        premium = item.get('premium', 0)
        sentiment = item.get('sentiment', 'neutral')
        
        emoji = "🟢" if sentiment == 'bullish' else "🔴" if sentiment == 'bearish' else "⚪"
        
        summary += f"{emoji} {contract}:\n"
        summary += f"   {volume} contracts (${premium:,.0f} premium)\n"
    
    # Add overall analysis
    if overall_sentiment == "bullish":
        summary += "\nLarge traders are showing bullish sentiment with significant call buying."
    elif overall_sentiment == "bearish":
        summary += "\nLarge traders are showing bearish sentiment with significant put buying."
    else:
        summary += "\nMixed sentiment with balanced call and put activity."
    
    return summary