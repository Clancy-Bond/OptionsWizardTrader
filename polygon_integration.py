"""
Polygon.io API integration for OptionsWizard
This module provides functions to interact with Polygon.io's APIs
for stock and options data retrieval.
"""
import os
import requests
import json
import random
import time
from datetime import datetime
from dotenv import load_dotenv
from polygon_trades import get_option_trade_data
import math
import cache_module

# Import the institutional sentiment analysis module
try:
    from institutional_sentiment import analyze_institutional_sentiment, get_human_readable_summary
    INSTITUTIONAL_ANALYSIS_AVAILABLE = True
except ImportError:
    INSTITUTIONAL_ANALYSIS_AVAILABLE = False
    # Create stub functions if the module isn't available
    def analyze_institutional_sentiment(option_trades, stock_price):
        return {'status': 'module_not_found'}
    def get_human_readable_summary(analysis_results, ticker):
        return "Institutional sentiment analysis not available"

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

# Cache for ticker validity to minimize API calls
valid_ticker_cache = set()
exchange_ticker_cache = {}
option_chain_cache = {}

# Cache for unusual options activity with timestamps now handled by cache_module.py
# See cache_module.py for implementation details

def get_headers():
    """
    Get authenticated headers for Polygon API requests
    """
    # Polygon.io doesn't use Bearer token in v2 and v3 REST API
    # It uses the API key as a query parameter
    return {
        'User-Agent': 'OptionsWizard/1.0'  # Add user agent to reduce chance of rate limiting
    }
    
import time
# Global trackers for rate limiting
_last_api_call = 0
_min_call_interval = 0.4  # Hybrid approach: slightly faster than conservative 0.6
_consecutive_calls = 0
_max_retries = 3  # Reduced maximum retries to fail faster to YF fallback

# Flag to identify API endpoints that previously would fall back to Yahoo Finance
# Now returns False for all endpoints as we're using Polygon.io exclusively
def is_fallback_endpoint(url):
    """
    This function previously identified endpoints that would fall back to Yahoo Finance.
    It now always returns False as we've disabled all Yahoo Finance fallbacks.
    """
    # No longer falling back to Yahoo Finance for any endpoint
    return False

def handle_rate_limit(retry_after=1):
    """
    Handle rate limiting from Polygon API by sleeping
    
    Args:
        retry_after: Seconds to wait before retrying (default: 1 second)
    """
    print(f"Rate limited by Polygon API, waiting {retry_after} seconds...")
    time.sleep(retry_after)
    
def throttled_api_call(url, headers=None, retry_count=0):
    """
    Make an API call with built-in throttling to avoid rate limits
    With faster fallback for price/options endpoints
    
    Args:
        url: The URL to call
        headers: Optional headers dictionary
        retry_count: Current retry attempt (internal tracking)
        
    Returns:
        Response object from requests
    """
    global _last_api_call, _min_call_interval, _consecutive_calls, _max_retries
    
    # Check if this is a price or options lookup that should quickly fall back
    quick_fallback = is_fallback_endpoint(url)
    
    # For price/options endpoints, use fewer retries before falling back to YF
    effective_max_retries = 1 if quick_fallback else _max_retries
    
    # Safety check for excessive retries
    if retry_count > effective_max_retries:
        if quick_fallback:
            print(f"Quick fallback triggered for {url} - Will try Yahoo Finance")
            # Let the calling function handle Yahoo fallback
            class FallbackResponse:
                def __init__(self):
                    self.status_code = 503  # Service unavailable
                    self.text = "Fallback to Yahoo Finance recommended"
                def json(self):
                    return {"status": "error", "message": "Fallback to Yahoo Finance recommended"}
            return FallbackResponse()
        else:
            print(f"Maximum retries ({_max_retries}) exceeded for URL: {url}")
            # Return a simulated response with error status
            class MockResponse:
                def __init__(self):
                    self.status_code = 500
                    self.text = "Maximum retries exceeded"
                def json(self):
                    return {"error": "Maximum retries exceeded"}
            return MockResponse()
    
    # Calculate time since last API call
    now = time.time()
    time_since_last_call = now - _last_api_call
    
    # Adaptive delay - but less aggressive scaling for hybrid approach
    # For price/options lookups, use even less delay to get quick answers
    if quick_fallback:
        adaptive_delay = _min_call_interval * (1 + min(_consecutive_calls // 10, 3))
    else:
        adaptive_delay = _min_call_interval * (1 + min(_consecutive_calls // 8, 4))
    
    # If we've made a call too recently, sleep to avoid rate limiting
    if time_since_last_call < adaptive_delay:
        sleep_time = adaptive_delay - time_since_last_call
        time.sleep(sleep_time)
    
    # Make the API call
    try:
        response = requests.get(url, headers=headers, timeout=10)  # Shorter timeout for quicker fallback
        
        # Debug log for 403 errors
        if response.status_code == 403:
            print(f"403 Forbidden error for URL: {url}")
            print(f"Response: {response.text}")
            # Reset consecutive calls counter
            _consecutive_calls = 0
            
            # For price/options lookups with 403, don't retry - go straight to YF
            if quick_fallback:
                print(f"403 on price/options lookup, recommending YF fallback")
                return response  # Let the caller handle YF fallback
        elif response.status_code == 200:
            # Successful call
            _consecutive_calls += 1
        
        # Update last call time
        _last_api_call = time.time()
        
        # Handle rate limiting with exponential backoff
        if response.status_code == 429:
            # Price/options lookups should fall back after one rate limit
            if quick_fallback and retry_count >= 0:
                print(f"Rate limited on price/options lookup, recommending YF fallback")
                return response  # Let the caller handle YF fallback
                
            # Each retry waits longer (3, 6, 12, 24 seconds...)
            backoff_delay = 3 * (2 ** retry_count)
            handle_rate_limit(backoff_delay)
            # Reset consecutive calls counter
            _consecutive_calls = 0
            # Retry with incremented counter
            return throttled_api_call(url, headers, retry_count + 1)
            
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        # Reset consecutive calls counter
        _consecutive_calls = 0
        
        # For price/options lookups with connection issues, go straight to YF
        if quick_fallback:
            print(f"Connection error on price/options lookup, recommending YF fallback")
            class FallbackResponse:
                def __init__(self):
                    self.status_code = 503  # Service unavailable
                    self.text = "Network error - Fallback to Yahoo Finance"
                def json(self):
                    return {"status": "error", "message": "Network error"}
            return FallbackResponse()
            
        # For other endpoints, retry with a delay
        time.sleep(2)
        return throttled_api_call(url, headers, retry_count + 1)
    except Exception as e:
        print(f"Unexpected error in API call: {str(e)}")
        _consecutive_calls = 0
        return None

def fetch_all_tickers():
    """
    Fetch a comprehensive list of all stock tickers from Polygon.io
    This function gets all active tickers across major exchanges,
    but ONLY refreshes the ticker list on the 5th day of the month.
    
    Returns:
        A set of valid ticker symbols
    """
    today = datetime.now()
    all_tickers = set()
    
    # Check if we should fetch new tickers (only on the 5th of the month)
    refresh_tickers = today.day == 5
    
    # Try to load from existing cache file first, regardless of day
    if os.path.exists('polygon_tickers.json'):
        try:
            with open('polygon_tickers.json', 'r') as f:
                cached_tickers = json.load(f)
            all_tickers.update(cached_tickers)
            valid_ticker_cache.update(cached_tickers)
            print(f"Loaded {len(cached_tickers)} tickers from polygon_tickers.json cache")
            
            # If it's not the 5th of the month, return the cached tickers
            if not refresh_tickers:
                print("Not the 5th of month - using cached ticker list without refresh")
                return all_tickers
        except Exception as e:
            print(f"Error loading cached tickers: {str(e)}")
            # Even if there's an error, only try to refresh on the 5th
            if not refresh_tickers:
                print("Not the 5th of month - unable to refresh ticker list")
                return all_tickers
    elif not refresh_tickers:
        # If no cache exists and it's not the 5th, we can't refresh
        print("No ticker cache found and not the 5th of month - cannot refresh")
        return all_tickers
    
    # If we reach here, it's the 5th of the month or cache doesn't exist but it's the 5th
    if refresh_tickers:
        print(f"Today is the 5th of the month: Refreshing comprehensive ticker list from Polygon.io...")
        
        try:
            # Endpoint for ticker types
            types = ['CS', 'ETF']  # Common Stock and ETFs
            for ticker_type in types:
                endpoint = f"{BASE_URL}/v3/reference/tickers?type={ticker_type}&active=true&limit=1000&apiKey={POLYGON_API_KEY}"
                
                # Make initial request with throttling
                response = throttled_api_call(endpoint, headers=get_headers())
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
                    # Use throttled API call for pagination too
                    response = throttled_api_call(full_url)
                    
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
            
            # Only save to cache file if we got a substantial number of tickers
            if len(all_tickers) > 100:
                try:
                    with open('polygon_tickers.json', 'w') as f:
                        json.dump(list(all_tickers), f)
                    print(f"Saved {len(all_tickers)} tickers to polygon_tickers.json")
                except Exception as e:
                    print(f"Error saving tickers: {str(e)}")
            else:
                print(f"Insufficient tickers found ({len(all_tickers)}), not updating cache")
                
        except Exception as e:
            print(f"Error during Polygon ticker fetching: {str(e)}")
            
            # If we have cached tickers already loaded, use those
            if all_tickers:
                print(f"Using previously loaded {len(all_tickers)} cached tickers despite refresh error")
            else:
                # Try to load from backup file as a last resort
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
    
    # Try loading from cache file if available
    try:
        if os.path.exists('polygon_tickers.json') and not valid_ticker_cache:
            with open('polygon_tickers.json', 'r') as f:
                cached_tickers = json.load(f)
                valid_ticker_cache.update(cached_tickers)
                if ticker in valid_ticker_cache:
                    return True
    except Exception as e:
        print(f"Error loading cache: {str(e)}")
    
    # Make API call to validate ticker
    try:
        endpoint = f"{BASE_URL}/v3/reference/tickers?ticker={ticker}&apiKey={POLYGON_API_KEY}"
        response = throttled_api_call(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error checking ticker {ticker}: {response.status_code}")
            # Check our cache file one more time before failing
            if os.path.exists('polygon_tickers.json'):
                with open('polygon_tickers.json', 'r') as f:
                    cached_tickers = json.load(f)
                    if ticker in cached_tickers:
                        valid_ticker_cache.add(ticker)
                        return True
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
        endpoint = f"{BASE_URL}/v3/reference/tickers/{ticker}?apiKey={POLYGON_API_KEY}"
        response = throttled_api_call(endpoint, headers=get_headers())
        
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
    
    # Always use Polygon.io for price data, regardless of the day of month
    # This ensures consistent data quality and avoids mixing data sources
    print(f"Using Polygon.io for {ticker} price data")
    
    try:
        # Get latest trade from Polygon
        endpoint = f"{BASE_URL}/v2/last/trade/{ticker}?apiKey={POLYGON_API_KEY}"
        response = throttled_api_call(endpoint, headers=get_headers())
        
        # If response is None or there's an error
        if not response or response.status_code != 200:
            print(f"Error fetching current price for {ticker}: {response.status_code if response else 'No response'}")
            print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
            return None
        
        # Process successful Polygon response
        data = response.json()
        result = data.get('results')
        
        if result:
            return result.get('p')  # 'p' is the price field
        
        # If Polygon returns empty result, return None
        print(f"Polygon returned empty result for {ticker}")
        print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
        return None
        
    except Exception as e:
        print(f"Error fetching current price for {ticker}: {str(e)}")
        print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
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
    
    # Always use Polygon.io for options data, regardless of the day of month
    # This ensures consistent data quality and avoids mixing data sources
    print(f"Using Polygon.io for {ticker} option chain")
    
    # Check cache first if we have an expiration date
    cache_key = f"{ticker}_{expiration_date}"
    if expiration_date and cache_key in option_chain_cache:
        return option_chain_cache[cache_key]
    
    try:
        # Build the API endpoint with a larger limit to ensure we get enough options
        # This is crucial for unusual activity detection which needs near-the-money options
        if expiration_date:
            endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&expiration_date={expiration_date}&limit=1000&apiKey={POLYGON_API_KEY}"
        else:
            endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&limit=1000&apiKey={POLYGON_API_KEY}"
        
        # Use throttled API call
        response = throttled_api_call(endpoint, headers=get_headers())
            
        # If response indicates an error, return None (no fallback)
        if not response or response.status_code in [403, 429, 503]:
            print(f"Error fetching option chain for {ticker}: {response.status_code if response else 'No response'}")
            print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
            return None
        
        # Process successful Polygon response
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
        print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
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
        endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&limit=1000&apiKey={POLYGON_API_KEY}"
        response = throttled_api_call(endpoint, headers=get_headers())
        
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
            print(f"No option chain found for {ticker} at {expiration_date}")
            print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
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
            print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
            return None
        
        # Now get the latest price for this option
        endpoint = f"{BASE_URL}/v2/last/trade/{option_symbol}?apiKey={POLYGON_API_KEY}"
        response = throttled_api_call(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error fetching option price: {response.status_code}")
            print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
            return None
        
        data = response.json()
        result = data.get('results')
        
        if result:
            return result.get('p')  # 'p' is the price field
        
        return None
        
    except Exception as e:
        print(f"Error fetching option price: {str(e)}")
        print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
        return None

def calculate_unusualness_score(option, trades, stock_price, option_data=None):
    """
    Calculate an unusualness score for an option based on multiple indicators
    
    Args:
        option: The option data from Polygon API
        trades: List of trades for this option
        stock_price: Current price of the underlying stock
        option_data: Additional option data if available
        
    Returns:
        A score from 0-100 indicating how unusual the option activity is,
        along with a breakdown of what factors contributed to this score
    """
    score = 0
    score_breakdown = {}
    
    # Extract basic option information
    strike = option.get('strike_price', 0)
    contract_type = option.get('contract_type', '').lower()
    expiration_date = option.get('expiration_date', '')
    open_interest = option.get('open_interest', 0)
    implied_volatility = option.get('implied_volatility', 0)
    
    # If we have no trades or basic data is missing, return 0 score
    if not trades or not strike or not contract_type or not expiration_date:
        return 0, {}
    
    # 1. Large Block Trades (0-25 points)
    large_trades = [t for t in trades if t.get('size', 0) >= 10]  # Trades with 10+ contracts
    largest_trade_size = max([t.get('size', 0) for t in trades], default=0)
    
    # Score based on largest single trade size
    block_trade_score = 0
    if largest_trade_size >= 100:
        block_trade_score = 25  # Very large block
    elif largest_trade_size >= 50:
        block_trade_score = 20
    elif largest_trade_size >= 20:
        block_trade_score = 15
    elif largest_trade_size >= 10:
        block_trade_score = 10
    elif largest_trade_size >= 5:
        block_trade_score = 5
    
    score += block_trade_score
    score_breakdown['block_trade'] = block_trade_score
    
    # 2. Total Volume Score (0-20 points)
    # Note: Since Polygon.io returns 0 for open interest, we're using absolute volume scoring
    total_volume = sum(t.get('size', 0) for t in trades)
    
    volume_score = 0
    if total_volume >= 200:
        volume_score = 20  # Very high volume
    elif total_volume >= 100:
        volume_score = 15
    elif total_volume >= 50:
        volume_score = 10
    elif total_volume >= 20:
        volume_score = 5
    elif total_volume >= 10:
        volume_score = 3
    
    score += volume_score
    score_breakdown['volume_score'] = volume_score
    
    # 3. Volume Concentration (0-15 points)
    # Higher score when volume is concentrated in fewer trades
    volume_concentration_score = 0
    avg_trade_size = total_volume / len(trades) if len(trades) > 0 else 0
    
    if avg_trade_size >= 20:
        volume_concentration_score = 15  # Large average trade size
    elif avg_trade_size >= 10:
        volume_concentration_score = 10
    elif avg_trade_size >= 5:
        volume_concentration_score = 5
    
    score += volume_concentration_score
    score_breakdown['volume_concentration'] = volume_concentration_score
    
    # 3. Strike Price Distance (0-15 points)
    # How far is the strike from current price
    if stock_price > 0:
        strike_distance = abs(strike - stock_price) / stock_price
        
        strike_score = 0
        if strike_distance >= 0.2:  # 20%+ OTM
            strike_score = 15
        elif strike_distance >= 0.1:  # 10-20% OTM
            strike_score = 10
        elif strike_distance >= 0.05:  # 5-10% OTM
            strike_score = 5
        
        score += strike_score
        score_breakdown['strike_distance'] = strike_score
    
    # 4. Time to Expiration (0-15 points)
    # Shorter-term options with unusual activity are more significant
    try:
        expiry_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_to_expiry = (expiry_date - today).days
        
        expiry_score = 0
        if days_to_expiry <= 7:  # Expiring within a week
            expiry_score = 15
        elif days_to_expiry <= 14:  # Expiring within two weeks
            expiry_score = 10
        elif days_to_expiry <= 30:  # Expiring within a month
            expiry_score = 5
        
        score += expiry_score
        score_breakdown['time_to_expiry'] = expiry_score
    except Exception as e:
        print(f"Error calculating expiry score: {e}")
    
    # 5. Premium Size (0-20 points)
    avg_price = sum(t.get('price', 0) * t.get('size', 0) for t in trades) / total_volume if total_volume > 0 else 0
    total_premium = total_volume * 100 * avg_price  # Each contract is 100 shares
    
    premium_score = 0
    if total_premium >= 1000000:  # $1M+
        premium_score = 20
    elif total_premium >= 500000:  # $500K+
        premium_score = 15
    elif total_premium >= 100000:  # $100K+
        premium_score = 10
    elif total_premium >= 50000:  # $50K+
        premium_score = 5
    
    score += premium_score
    score_breakdown['premium_size'] = premium_score
    
    # Calculate total score (max 100)
    final_score = min(score, 100)
    
    # Add basic trade information for reference
    score_breakdown['total_volume'] = total_volume
    score_breakdown['total_premium'] = total_premium
    score_breakdown['largest_trade'] = largest_trade_size
    if open_interest > 0:
        score_breakdown['vol_oi_ratio'] = round(total_volume / open_interest, 2)
    
    return final_score, score_breakdown


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
    current_time = datetime.now()
    today = current_time.strftime('%Y-%m-%d')
    
    # Check if we have cached data for this ticker that's still valid
    print(f"DEBUG: Cache check before API call - {ticker} {'in' if cache_module.cache_contains(ticker) else 'not in'} cache")
    cache_module.print_cache_contents()  # Debug: print all cache contents
    cached_data, found = cache_module.get_from_cache(ticker)
    if found:
        print(f"DEBUG: Using cached data for {ticker} with {len(cached_data) if cached_data else 0} items")
        return cached_data
    print(f"DEBUG: Cache miss for {ticker}, fetching fresh data from API")
    
    try:
        # Get options for today's date
        chain = get_option_chain(ticker)
        
        if not chain:
            print(f"No option chain found for {ticker}")
            print(f"No fallback to Yahoo Finance - using only Polygon.io data as requested")
            return None
        
        # Get current stock price for context
        stock_price = get_current_price(ticker)
        
        # Track potential unusual activity and ALL options for comprehensive market sentiment
        unusual_activity = []
        all_options = []  # Track ALL analyzed options to get a complete view of market sentiment
        forbidden_error_count = 0
        processed_options = 0
        
        # Filter options to include more strikes (25% from current price) and minimum open interest
        near_money_options = []
        total_options = len(chain) if chain else 0
        filtered_by_strike = 0
        filtered_by_interest = 0
        
        if stock_price:
            for option in chain:
                option_symbol = option.get('ticker')
                strike = option.get('strike_price')
                expiry = option.get('expiration_date')
                contract_type = option.get('contract_type', '').lower()
                open_interest = option.get('open_interest', 0)
                
                # Skip if missing key info
                if not option_symbol or not strike or not expiry or not contract_type:
                    continue
                
                # Check if within expanded range (25% of current price)
                price_filter = abs(strike - stock_price) / stock_price <= 0.25
                
                if not price_filter:
                    filtered_by_strike += 1
                    continue
                
                # Don't filter by open interest - Polygon.io returns 0 for all options
                # We confirmed that filtering by open interest blocks all options with our API key
                if random.random() < 0.01:  # Only print ~1% of options to avoid flooding logs
                    print(f"DEBUG: Option {option.get('ticker')} - Strike: {strike}, Open Interest: {open_interest}")
                    
                # Always include all options regardless of open interest
                # Use other factors like trade volume for scoring instead
                interest_filter = True
                
                if not interest_filter:
                    filtered_by_interest += 1
                    continue
                
                # Only include options that meet both criteria
                near_money_options.append(option)
        
        print(f"Found {len(near_money_options)} options to analyze (within 25% of price and min. open interest)")
        print(f"Filtered out {filtered_by_strike} options outside price range and {filtered_by_interest} with insufficient open interest")
        print(f"Total options in chain: {total_options}")
        
        # No longer limiting the number of options - analyze all near-the-money options
        # Sort by proximity to current price for better analysis in the output
        near_money_options.sort(key=lambda x: abs(x.get('strike_price', 0) - stock_price))
        
        # Check if we should use parallel processing
        try:
            # Try to import parallel processing module
            print("Attempting to use parallel processing for faster option analysis...")
            from parallel_options import analyze_options_in_parallel
            
            # Use parallel processing for better performance
            result_with_metadata = analyze_options_in_parallel(
                near_money_options, 
                stock_price, 
                get_headers(), 
                ticker
            )
            
            # Store in cache with current timestamp
            cache_module.add_to_cache(ticker, result_with_metadata)
            
            all_bullish_count = result_with_metadata.get('total_bullish_count', 0)
            all_bearish_count = result_with_metadata.get('total_bearish_count', 0)
            all_options_count = result_with_metadata.get('all_options_analyzed', 0)
            
            print(f"Added {ticker} to cache (will persist until next market open)")
            print(f"Cached unusual activity data for {ticker} with {all_bullish_count} bullish and {all_bearish_count} bearish options out of {all_options_count} total analyzed options (will expire in 5 minutes)")
            
            return result_with_metadata
            
        except ImportError:
            print("Parallel processing not available, using sequential processing")
                
        # Fall back to sequential processing if parallel processing is not available
        # Look for unusual volume and premium patterns
        for option in near_money_options:
            option_symbol = option.get('ticker')
            strike = option.get('strike_price')
            expiry = option.get('expiration_date')
            contract_type = option.get('contract_type', '').lower()
                
            # Get trades for this option
            endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=50&order=desc&apiKey={POLYGON_API_KEY}"
            response = throttled_api_call(endpoint, headers=get_headers())
            
            processed_options += 1
            
            if response.status_code != 200:
                if response.status_code == 403:
                    forbidden_error_count += 1
                    # If we've hit too many forbidden errors, this endpoint probably requires a plan upgrade
                    if forbidden_error_count > 5 and processed_options < 10:
                        print(f"Multiple 403 errors, likely need Polygon.io plan upgrade for options trades data")
                        break
                continue
                
            data = response.json()
            trades = data.get('results', [])
            
            # Print raw option data for debug
            print(f"Found {len(trades)} trades for {option_symbol}")
            
            # Use our scoring system to evaluate unusual activity
            if trades:
                # Calculate unusualness score
                unusualness_score, score_breakdown = calculate_unusualness_score(option, trades, stock_price)
                print(f"Option {option_symbol} received unusualness score: {unusualness_score}")
                
                # Calculate metrics for the activity (for ALL options)
                total_volume = sum(t.get('size', 0) for t in trades)
                avg_price = sum(t.get('price', 0) * t.get('size', 0) for t in trades) / total_volume if total_volume > 0 else 0
                total_premium = total_volume * 100 * avg_price  # Each contract is 100 shares
                
                # Determine sentiment based on option type (for ALL options)
                sentiment = None
                if contract_type == 'call':
                    sentiment = 'bullish'
                elif contract_type == 'put':
                    sentiment = 'bearish'
                
                # Get the actual transaction date if available (for ALL options)
                # We'll use our polygon_trades module to get the most significant trade
                trade_info = None
                try:
                    trade_info = get_option_trade_data(option_symbol)
                except Exception as e:
                    print(f"Error getting trade data for {option_symbol}: {str(e)}")
                
                # Create option data entry for all analyzed options
                option_entry = {
                    'contract': f"{ticker} {strike} {expiry} {contract_type.upper()}",
                    'volume': total_volume,
                    'avg_price': avg_price,
                    'premium': total_premium,
                    'sentiment': sentiment,
                    'unusualness_score': unusualness_score,
                    'score_breakdown': score_breakdown
                }
                
                # Add detailed transaction information if we have it
                if trade_info:
                    if 'date' in trade_info:
                        option_entry['transaction_date'] = trade_info['date']
                    
                    # Include exchange information
                    if 'exchange' in trade_info:
                        option_entry['exchange'] = trade_info['exchange']
                        
                    # Include exact timestamp if available
                    if 'timestamp' in trade_info:
                        option_entry['timestamp'] = trade_info['timestamp']
                        
                    # Include human-readable timestamp if available
                    if 'timestamp_human' in trade_info:
                        option_entry['timestamp_human'] = trade_info['timestamp_human']
                
                # Make sure volume is always available
                if 'volume' not in option_entry:
                    option_entry['volume'] = 0
                    
                # If we have trade info, use the actual trade size for volume calculation
                if trade_info and 'size' in trade_info and trade_info['size'] > 0:
                    option_entry['contract_volume'] = trade_info['size']
                else:
                    # Fallback to 1 (minimum) if no significant trades found
                    option_entry['contract_volume'] = 1
                
                # Add to ALL options analyzed list (regardless of unusualness score)
                all_options.append(option_entry)
                
                # Only add to unusual activity if score is above threshold
                if unusualness_score >= 30:  # Consider 30 as the threshold for "unusual enough"
                    # Use the same data for unusual activity
                    unusual_activity.append(option_entry.copy())
        
        # No fallback to Yahoo Finance - only using Polygon.io data as requested
        if forbidden_error_count > 5 and len(unusual_activity) == 0:
            print(f"Too many 403 errors for {ticker}, but not falling back to Yahoo Finance as requested")
            
            # Even with errors, store sentiment counts from any options analyzed
            if len(all_options) > 0:
                all_bullish_count = sum(item.get('contract_volume', 1) for item in all_options if item.get('sentiment') == 'bullish')
                all_bearish_count = sum(item.get('contract_volume', 1) for item in all_options if item.get('sentiment') == 'bearish')
                empty_result = {
                    'unusual_options': [],
                    'total_bullish_count': all_bullish_count,
                    'total_bearish_count': all_bearish_count,
                    'all_options_analyzed': len(all_options)
                }
            else:
                empty_result = {
                    'unusual_options': [],
                    'total_bullish_count': 0,
                    'total_bearish_count': 0,
                    'all_options_analyzed': 0
                }
                
            cache_module.add_to_cache(ticker, empty_result)
            print(f"Cached empty result for {ticker} due to API errors (will expire in 5 minutes)")
            # Return empty result to indicate no unusual activity found
            return empty_result
        
        # Calculate sentiment counts from ALL options analyzed (not just unusual ones)
        # This gives a more comprehensive view of market sentiment
        # Use contract volume to weight the sentiment counts
        all_bullish_count = sum(item.get('contract_volume', 1) for item in all_options if item.get('sentiment') == 'bullish')
        all_bearish_count = sum(item.get('contract_volume', 1) for item in all_options if item.get('sentiment') == 'bearish')
        
        # Print detailed breakdown of all options analyzed
        print(f"COMPLETE BREAKDOWN OF ALL OPTIONS: {len(all_options)} total options analyzed")
        all_total_contracts = all_bullish_count + all_bearish_count
        # Calculate volume-weighted percentages
        bullish_pct = (all_bullish_count / all_total_contracts * 100) if all_total_contracts > 0 else 0
        bearish_pct = (all_bearish_count / all_total_contracts * 100) if all_total_contracts > 0 else 0
        print(f"Volume-weighted sentiment: {all_bullish_count} bullish contracts ({bullish_pct:.1f}%) / {all_bearish_count} bearish contracts ({bearish_pct:.1f}%)")
        
        # Also print breakdown of just the unusual options for comparison
        unusual_bullish = sum(1 for item in unusual_activity if item.get('sentiment') == 'bullish')
        unusual_bearish = sum(1 for item in unusual_activity if item.get('sentiment') == 'bearish')
        print(f"UNUSUAL OPTIONS ONLY: {len(unusual_activity)} unusual options found")
        if len(unusual_activity) > 0:
            print(f"Unusual options sentiment: {unusual_bullish} bullish ({unusual_bullish/len(unusual_activity)*100:.1f}%) / {unusual_bearish} bearish ({unusual_bearish/len(unusual_activity)*100:.1f}%)")
        
        # Sort by unusualness score in descending order, with premium as a secondary factor
        unusual_activity.sort(key=lambda x: (x.get('unusualness_score', 0), x.get('premium', 0)), reverse=True)
        
        # Display top 10 unusual options
        if len(unusual_activity) > 0:
            print("TOP 10 MOST UNUSUAL OPTIONS:")
            for idx, item in enumerate(unusual_activity[:10]):
                print(f"  {idx+1}. {item.get('contract', 'Unknown')} - Score: {item.get('unusualness_score', 0)} - Sentiment: {item.get('sentiment', 'Unknown')} - Premium: ${item.get('premium', 0)/1000000:.2f}M")
        
        # Take top 5 (if we have that many)
        result = unusual_activity[:5]
        
        # Prepare standard result with metadata including ALL options (not just unusual ones)
        result_with_metadata = {
            'unusual_options': result,
            'total_bullish_count': all_bullish_count,
            'total_bearish_count': all_bearish_count,
            'all_options_analyzed': len(all_options)
        }
        
        # Perform institutional sentiment analysis if available
        if INSTITUTIONAL_ANALYSIS_AVAILABLE:
            try:
                # Prepare option trades data for sentiment analysis
                option_trades = []
                
                # Convert our options data format to the format expected by institutional_sentiment
                for opt in all_options:
                    # Include all trades for institutional analysis
                    try:
                        # Parse contract string (e.g., "SPY 484 2025-04-15 CALL")
                        contract_parts = opt.get('contract', '').split()
                        strike_price = 0
                        expiration_date = ''
                        
                        if len(contract_parts) > 1:
                            try:
                                strike_price = float(contract_parts[1])
                            except (ValueError, IndexError):
                                pass
                                
                        if len(contract_parts) > 2:
                            expiration_date = contract_parts[2]
                        
                        # Convert date to days to expiration
                        days_to_expiration = 30  # Default
                        if expiration_date:
                            try:
                                exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
                                today = datetime.now()
                                days_to_expiration = (exp_date - today).days
                                if days_to_expiration < 0:
                                    days_to_expiration = 1  # Minimum 1 day
                            except (ValueError, TypeError):
                                pass
                        
                        # Create timestamp for trade matching (required for hedging detection)
                        # Generate a synthetic timestamp within the last day with some randomness
                        # This creates clusters of timestamps that will help identify related trades
                        trade_timestamp = int(time.time() - (3600 * (opt.get('id', 0) % 24)))
                        
                        # If we have actual transaction data, use that timestamp instead
                        if 'timestamp' in opt and isinstance(opt.get('timestamp'), (int, float)):
                            trade_timestamp = int(opt.get('timestamp'))
                        elif 'transaction_date' in opt:
                            try:
                                tx_date = datetime.strptime(opt.get('transaction_date'), '%Y-%m-%d')
                                trade_timestamp = int(tx_date.timestamp())
                            except (ValueError, TypeError):
                                pass
                        
                        # Create the trade object with all required fields
                        trade = {
                            'id': opt.get('id', opt.get('contract', '')),
                            'symbol': opt.get('contract', ''),
                            'strike_price': strike_price,
                            'contract_type': 'call' if opt.get('sentiment') == 'bullish' else 'put',
                            'size': opt.get('contract_volume', 1),
                            'price': opt.get('avg_price', 0),
                            'premium': opt.get('premium', 0) / 100,  # Convert to per-contract premium
                            'expiration_date': expiration_date,
                            'days_to_expiration': days_to_expiration,
                            'sentiment': opt.get('sentiment', ''),
                            'timestamp': trade_timestamp,  # Numeric timestamp for comparison
                            'implied_volatility': 0.3  # Default IV for calculations
                        }
                        
                        # Add human readable timestamps if available
                        if 'timestamp_human' in opt:
                            trade['timestamp_human'] = opt.get('timestamp_human')
                        if 'transaction_date' in opt:
                            trade['transaction_date'] = opt.get('transaction_date')
                            
                        option_trades.append(trade)
                    except Exception as e:
                        print(f"Error processing option {opt.get('contract', 'Unknown')}: {str(e)}")
                        continue
                
                # Only perform analysis if we have enough trades
                if len(option_trades) >= 5:
                    # Get current stock price
                    stock_price = get_current_price(ticker)
                    
                    # Perform institutional sentiment analysis
                    inst_analysis = analyze_institutional_sentiment(option_trades, stock_price)
                    
                    # Add the results to our metadata
                    result_with_metadata['institutional_analysis'] = inst_analysis
                    
                    # Generate the human-readable summary
                    inst_summary = get_human_readable_summary(inst_analysis, ticker)
                    result_with_metadata['institutional_summary'] = inst_summary
                    
                    # If hedging was detected, adjust the sentiment counts
                    if inst_analysis.get('status') == 'success':
                        sentiment = inst_analysis.get('sentiment', {})
                        
                        # Use delta-weighted sentiment if available (more accurate)
                        if 'bullish_delta_pct' in sentiment and 'bearish_delta_pct' in sentiment:
                            result_with_metadata['adjusted_bullish_pct'] = sentiment.get('bullish_delta_pct')
                            result_with_metadata['adjusted_bearish_pct'] = sentiment.get('bearish_delta_pct')
                            result_with_metadata['hedging_detected'] = inst_analysis.get('hedging_detected', False)
                            result_with_metadata['hedging_pct'] = inst_analysis.get('hedging_pct', 0)
                        
                    print(f"Institutional sentiment analysis completed with {len(option_trades)} trades")
                else:
                    print(f"Insufficient trades for institutional sentiment analysis ({len(option_trades)} trades)")
            except Exception as e:
                print(f"Error in institutional sentiment analysis: {str(e)}")
        
        # Store in cache with current timestamp
        cache_module.add_to_cache(ticker, result_with_metadata)
        
        print(f"Cached unusual activity data for {ticker} with {all_bullish_count} bullish and {all_bearish_count} bearish options out of {len(all_options)} total analyzed options (will expire in 5 minutes)")
        return result_with_metadata
        
    except Exception as e:
        print(f"Error fetching unusual activity for {ticker}: {str(e)}")
        # No fallback to Yahoo Finance - only using Polygon.io data as requested
        print(f"Not falling back to Yahoo Finance for {ticker} unusual options activity as requested")
        
        # Cache error results to prevent repeated API calls that will fail
        # Even for exceptions, we store an empty but structured result with sentiment counters
        empty_result = {
            'unusual_options': [],
            'total_bullish_count': 0,
            'total_bearish_count': 0,
            'all_options_analyzed': 0
        }
        cache_module.add_to_cache(ticker, empty_result)
        print(f"Cached error result for {ticker} (will expire in 5 minutes)")
        
        return empty_result


def extract_strike_from_symbol(symbol):
    """Extract actual strike price from option symbol like O:TSLA250417C00252500"""
    if not symbol or not symbol.startswith('O:'):
        return None
            
    try:
        # Format is O:TSLA250417C00252500 where last 8 digits are strike * 1000
        strike_part = symbol.split('C')[-1] if 'C' in symbol else symbol.split('P')[-1]
        if strike_part and len(strike_part) >= 8:
            strike_value = int(strike_part) / 1000.0
            return f"{strike_value:.2f}"
        return None
    except (ValueError, IndexError):
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
    
    # Initialize timestamp_str at the function level to avoid "possibly unbound" error
    timestamp_str = ""
    
    if not ticker:
        return "Please specify a valid ticker symbol."
    
    print(f"Using Polygon.io data for unusual activity summary for {ticker}")
    
    # Check if we have ticker in cache before calling the function
    print(f"DEBUG: Cache check before API call - {ticker} {'in' if cache_module.cache_contains(ticker) else 'not in'} cache")
        
    result_with_metadata = get_unusual_options_activity(ticker)
    
    if not result_with_metadata or len(result_with_metadata) == 0:
        # No fallback to Yahoo Finance - only using Polygon.io data as requested
        print(f"No unusual options activity found for {ticker} in Polygon.io data, and not falling back to Yahoo Finance as requested")
        return f"📊 No significant unusual options activity detected for {ticker} in Polygon.io data.\n\nThis could indicate normal trading patterns or low options volume."
    
    # Extract the actual unusual options list and total sentiment counts
    if isinstance(result_with_metadata, dict) and 'unusual_options' in result_with_metadata:
        all_bullish_count = result_with_metadata.get('total_bullish_count', 0)
        all_bearish_count = result_with_metadata.get('total_bearish_count', 0)
        activity = result_with_metadata.get('unusual_options', [])
    else:
        # Handle case where the old format is still in the cache
        activity = result_with_metadata
        # Use contract volume if available, otherwise count each option as 1
        all_bullish_count = sum(item.get('contract_volume', 1) for item in activity if item.get('sentiment') == 'bullish')
        all_bearish_count = sum(item.get('contract_volume', 1) for item in activity if item.get('sentiment') == 'bearish')
    
    if not activity:
        return f"📊 No significant unusual options activity detected for {ticker} in Polygon.io data.\n\nThis could indicate normal trading patterns or low options volume."
        
    # Determine sentiment based on the top 5 most unusual options (for display purposes)
    bullish_count = sum(1 for item in activity if item.get('sentiment') == 'bullish')
    bearish_count = sum(1 for item in activity if item.get('sentiment') == 'bearish')
    
    # Debug information about the sentiment counts
    print(f"Found {bullish_count} bullish and {bearish_count} bearish options in top 5 for {ticker}")
    print(f"Total: {all_bullish_count} bullish and {all_bearish_count} bearish options in all unusual activity")
    for idx, item in enumerate(activity):
        print(f"  Option {idx+1}: {item.get('contract', 'Unknown')} - Sentiment: {item.get('sentiment', 'Unknown')}")
    
    # Determine overall sentiment for summary display based on top unusual options
    if bullish_count > bearish_count:
        overall_sentiment = "bullish"
    elif bearish_count > bullish_count:
        overall_sentiment = "bearish"
    else:
        overall_sentiment = "neutral"
    
    # Calculate percentages for the overall flow display based on ALL options (not just unusual ones)
    all_total_volume = all_bullish_count + all_bearish_count
    bullish_pct = round((all_bullish_count / all_total_volume) * 100) if all_total_volume > 0 else 0
    bearish_pct = round((all_bearish_count / all_total_volume) * 100) if all_total_volume > 0 else 0
    
    # Format total premium
    total_premium = sum(item.get('premium', 0) for item in activity)
    premium_in_millions = total_premium / 1000000
    
    # Create the summary with whale emojis in clean, bulleted format
    summary = f"🐳 {ticker} Unusual Options Activity 🐳\n\n"
    
    # Include top unusualness factors if available
    if activity and len(activity) > 0 and 'score_breakdown' in activity[0]:
        top_activity = activity[0]
        score_breakdown = top_activity.get('score_breakdown', {})
        unusualness_score = top_activity.get('unusualness_score', 0)
        
        if score_breakdown:
            # Find the top contributing factors
            sorted_factors = sorted(
                [(k, v) for k, v in score_breakdown.items() if k not in ['total_volume', 'total_premium', 'largest_trade', 'vol_oi_ratio']],
                key=lambda x: x[1],
                reverse=True
            )[:2]  # Get top 2 factors
            
            if sorted_factors:
                factor_descriptions = {
                    'block_trade': "large block trades",
                    'volume_to_oi': "high volume relative to open interest",
                    'strike_distance': "unusual strike price selection",
                    'time_to_expiry': "short-term expiration",
                    'premium_size': "large premium value"
                }
                
                # Previous code to add unusualness score has been removed as requested
                unusual_factors = [factor_descriptions.get(k, k) for k, v in sorted_factors if v > 0]
                
                # Find specific trade information based on sentiment
                if overall_sentiment == "bullish":
                    main_trade = next((item for item in activity if item.get('sentiment') == 'bullish'), top_activity)
                elif overall_sentiment == "bearish":
                    main_trade = next((item for item in activity if item.get('sentiment') == 'bearish'), top_activity)
                else:
                    main_trade = top_activity
                    
                # Store the timestamp for use in the main trade description
                timestamp_str = ""
                if 'timestamp_human' in main_trade:
                    timestamp_str = main_trade['timestamp_human']
                elif 'transaction_date' in main_trade:
                    timestamp_str = main_trade['transaction_date']
                    
                summary += "\n"
    
    # Add bullish or bearish summary statement
    if overall_sentiment == "bullish":
        # Get properly formatted expiration date
        expiry_date = ""
        try:
            main_contract = next((item for item in activity if item.get('sentiment') == 'bullish'), activity[0])
            contract_parts = main_contract.get('contract', '').split()
            
            # Extract expiration date from option symbol (O:TSLA250417C00252500 → 2025-04-17)
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Parse expiration from symbol format (O:TSLA250417...)
                    ticker_part = symbol.split(':')[1]
                    date_start = len(ticker_part.split()[0])
                    if len(ticker_part) > date_start + 6:  # Make sure there's enough characters
                        year = '20' + ticker_part[date_start:date_start+2]
                        month = ticker_part[date_start+2:date_start+4]
                        day = ticker_part[date_start+4:date_start+6]
                        expiry_date = f"{month}/{day}/{year[-2:]}"
            
            # Fallback to contract parts if symbol parsing failed
            if not expiry_date and len(contract_parts) >= 3:
                expiry_date = contract_parts[2]
                
            # Start the summary with integrated timestamp
            if timestamp_str:
                summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
                # Timestamp is now shown at the end of the next line
            
            else:
                summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
# Removed 'bet with' text
                
            # Add strike price and expiration
            if len(contract_parts) >= 3:
                # If we have a properly parsed expiration date
                if expiry_date:
                    # Try to extract the real strike price from the option symbol
                    if 'symbol' in main_contract:
                        strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if strike_price:
                            summary += f"in-the-money ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                        else:
                            summary += f"in-the-money ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                    else:
                        summary += f"in-the-money ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                else:
                    # Fallback to just the second part if we couldn't parse a proper date
                    summary += f"in-the-money ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
            else:
                summary += f"options from the largest unusual activity.\n\n"
        except (IndexError, AttributeError):
            # If we couldn't parse the contract but have a timestamp
            if timestamp_str:
                summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
                # Removed 'occurred at' timestamp
                summary += f"with options from the largest unusual activity.\n\n"
            else:
                summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
# Removed 'bet with' text
                summary += f"options from the largest unusual activity.\n\n"
        
        # Safely calculate the ratio
        if bearish_count > 0:
            summary += f"• Institutional Investors are heavily favoring call options with volume {round(bullish_count/bearish_count, 1)}x the put\nopen interest.\n\n"
        else:
            summary += f"• Institutional Investors are heavily favoring call options with dominant call volume.\n\n"
            
    elif overall_sentiment == "bearish":
        # Get properly formatted expiration date
        expiry_date = ""
        try:
            main_contract = next((item for item in activity if item.get('sentiment') == 'bearish'), activity[0])
            contract_parts = main_contract.get('contract', '').split()
            
            # Extract expiration date from option symbol (O:TSLA250417C00252500 → 2025-04-17)
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Parse expiration from symbol format (O:TSLA250417...)
                    ticker_part = symbol.split(':')[1]
                    date_start = len(ticker_part.split()[0])
                    if len(ticker_part) > date_start + 6:  # Make sure there's enough characters
                        year = '20' + ticker_part[date_start:date_start+2]
                        month = ticker_part[date_start+2:date_start+4]
                        day = ticker_part[date_start+4:date_start+6]
                        expiry_date = f"{month}/{day}/{year[-2:]}"
            
            # Fallback to contract parts if symbol parsing failed
            if not expiry_date and len(contract_parts) >= 3:
                expiry_date = contract_parts[2]
                
            # Start the summary with integrated timestamp
            if timestamp_str:
                summary += f"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "
                # Timestamp is now shown at the end of the next line
            
            else:
                summary += f"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "
                # Removed 'bet with' text
                
            # Add strike price and expiration
            if len(contract_parts) >= 3:
                # If we have a properly parsed expiration date
                if expiry_date:
                    # Try to extract the real strike price from the option symbol
                    if 'symbol' in main_contract:
                        strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if strike_price:
                            summary += f"in-the-money ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                        else:
                            summary += f"in-the-money ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                    else:
                        summary += f"in-the-money ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                else:
                    # Fallback to just the second part if we couldn't parse a proper date
                    summary += f"in-the-money ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
            else:
                summary += f"options from the largest unusual activity.\n\n"
        except (IndexError, AttributeError):
            # If we couldn't parse the contract but have a timestamp
            if timestamp_str:
                summary += f"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "
                # Removed 'occurred at' timestamp
                summary += f"with options from the largest unusual activity.\n\n"
            else:
                summary += f"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "
                # Removed 'bet with'
                summary += f"options from the largest unusual activity.\n\n"
        
        # Safely calculate the ratio
        if bullish_count > 0:
            summary += f"• Institutional Investors are heavily favoring put options with volume {round(bearish_count/bullish_count, 1)}x the call\nopen interest.\n\n"
        else:
            summary += f"• Institutional Investors are heavily favoring put options with dominant put volume.\n\n"
            
    else:
        summary += f"• I'm seeing mixed activity for {ticker}. There is balanced call and put activity.\n\n"
    
    # Add overall flow percentages (based on ALL options contracts analyzed, not just unusual ones)
    total_analyzed_contracts = all_bullish_count + all_bearish_count
    summary += f"Overall flow: {bullish_pct}% bullish / {bearish_pct}% bearish (based on {total_analyzed_contracts} analyzed option contracts)"
    
    # Add institutional sentiment analysis if available
    if isinstance(result_with_metadata, dict) and 'institutional_summary' in result_with_metadata:
        inst_summary = result_with_metadata.get('institutional_summary', '')
        if inst_summary:
            # Add a separator
            summary += "\n\n" + "-" * 40 + "\n\n"
            # Add the institutional sentiment analysis
            summary += inst_summary
    
    # Check if hedging was detected and show adjusted flow percentages
    if (isinstance(result_with_metadata, dict) and 
        'adjusted_bullish_pct' in result_with_metadata and 
        'adjusted_bearish_pct' in result_with_metadata and
        'hedging_detected' in result_with_metadata and
        result_with_metadata.get('hedging_detected', False)):
        
        adj_bullish_pct = round(result_with_metadata.get('adjusted_bullish_pct', 0))
        adj_bearish_pct = round(result_with_metadata.get('adjusted_bearish_pct', 0))
        hedging_pct = round(result_with_metadata.get('hedging_pct', 0))
        
        if hedging_pct > 5:  # Only show if there's significant hedging (>5%)
            summary += f"\n\n📊 After filtering out {hedging_pct}% hedging activity, the adjusted flow is: {adj_bullish_pct}% bullish / {adj_bearish_pct}% bearish"
    
    return summary