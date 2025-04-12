"""
Polygon.io API integration for OptionsWizard
This module provides functions to interact with Polygon.io's APIs
for stock and options data retrieval.
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from polygon_trades import get_option_trade_data

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

# Flag to identify API endpoints that should quickly fall back to Yahoo Finance
def is_fallback_endpoint(url):
    """Check if this URL is for an endpoint that should quickly fall back to YF"""
    # Check if this is a price lookup or options chain endpoint
    price_patterns = ['/last/trade/', '/last/quote/', '/v2/snapshot/']  
    options_patterns = ['/options/contracts', '/reference/options/']
    
    for pattern in price_patterns + options_patterns:
        if pattern in url:
            return True
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
    
    # First check if today is not the 5th of the month - directly use Yahoo Finance
    today = datetime.now()
    if today.day != 5:
        # On days other than the 5th, prefer Yahoo Finance to save Polygon API calls
        try:
            import yfinance as yf
            print(f"Using Yahoo Finance for {ticker} price data (not 5th of month)")
            stock = yf.Ticker(ticker)
            price = stock.info.get('regularMarketPrice')
            if price:
                return price
        except Exception as yf_error:
            print(f"Yahoo Finance price lookup failed: {str(yf_error)}")
            # Continue with Polygon as fallback if Yahoo fails
    
    try:
        # Get latest trade from Polygon
        endpoint = f"{BASE_URL}/v2/last/trade/{ticker}?apiKey={POLYGON_API_KEY}"
        response = throttled_api_call(endpoint, headers=get_headers())
        
        # If response is None or indicates we should use YF fallback
        if not response or response.status_code in [403, 429, 503]:
            print(f"Using Yahoo Finance fallback for {ticker} price data")
            try:
                import yfinance as yf
                stock = yf.Ticker(ticker)
                price = stock.info.get('regularMarketPrice')
                if price:
                    return price
            except Exception as yf_error:
                print(f"Yahoo Finance fallback also failed: {str(yf_error)}")
            return None
            
        # If any other error occurs with Polygon
        if response.status_code != 200:
            print(f"Error fetching current price for {ticker}: {response.status_code}")
            # Always try Yahoo Finance as fallback for any error
            try:
                import yfinance as yf
                print(f"Fallback to Yahoo Finance for {ticker} price data")
                stock = yf.Ticker(ticker)
                price = stock.info.get('regularMarketPrice')
                if price:
                    return price
            except Exception as yf_error:
                print(f"Yahoo Finance fallback also failed: {str(yf_error)}")
            return None
        
        # Process successful Polygon response
        data = response.json()
        result = data.get('results')
        
        if result:
            return result.get('p')  # 'p' is the price field
        
        # If Polygon returns empty result, try Yahoo
        print(f"Polygon returned empty result for {ticker}, trying Yahoo Finance")
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            price = stock.info.get('regularMarketPrice')
            if price:
                return price
        except Exception as yf_error:
            print(f"Yahoo Finance fallback also failed: {str(yf_error)}")
            
        return None
        
    except Exception as e:
        print(f"Error fetching current price for {ticker}: {str(e)}")
        
        # Always fall back to Yahoo Finance for any exception
        try:
            import yfinance as yf
            print(f"Exception fallback to Yahoo Finance for {ticker} price data")
            stock = yf.Ticker(ticker)
            price = stock.info.get('regularMarketPrice')
            if price:
                return price
        except Exception as yf_error:
            print(f"Yahoo Finance fallback also failed: {str(yf_error)}")
            
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
    
    # First check if today is not the 5th of the month - directly use Yahoo Finance for options
    today = datetime.now()
    if today.day != 5:
        # On days other than the 5th, prefer Yahoo Finance to save API calls
        try:
            import yfinance as yf
            import pandas as pd
            print(f"Using Yahoo Finance for {ticker} option chain (not 5th of month)")
            
            stock = yf.Ticker(ticker)
            
            # If we need specific expiration
            if expiration_date:
                try:
                    options = stock.option_chain(expiration_date)
                    # Convert Yahoo format to Polygon format
                    results = []
                    
                    # Process calls
                    for _, row in options.calls.iterrows():
                        results.append({
                            'ticker': f"{ticker}{expiration_date.replace('-', '')}C{int(row['strike']*1000)}",
                            'underlying_ticker': ticker,
                            'expiration_date': expiration_date,
                            'strike_price': float(row['strike']),
                            'contract_type': 'call',
                            'last_price': float(row['lastPrice']),
                            'volume': int(row['volume']),
                            'open_interest': int(row['openInterest'])
                        })
                    
                    # Process puts
                    for _, row in options.puts.iterrows():
                        results.append({
                            'ticker': f"{ticker}{expiration_date.replace('-', '')}P{int(row['strike']*1000)}",
                            'underlying_ticker': ticker,
                            'expiration_date': expiration_date,
                            'strike_price': float(row['strike']),
                            'contract_type': 'put',
                            'last_price': float(row['lastPrice']),
                            'volume': int(row['volume']),
                            'open_interest': int(row['openInterest'])
                        })
                    
                    # Cache the results
                    cache_key = f"{ticker}_{expiration_date}"
                    option_chain_cache[cache_key] = results
                    
                    return results
                except Exception as e:
                    print(f"Error getting Yahoo chain for specific expiration: {str(e)}")
                    # Continue with Polygon if this fails
            else:
                # If we just need available expirations
                expirations = stock.options
                if expirations:
                    # Get the first expiration's chain as an example
                    try:
                        options = stock.option_chain(expirations[0])
                        results = []
                        
                        # Process just a sample set to return format
                        for exp_date in expirations:
                            sample_call = {
                                'ticker': f"{ticker}{exp_date.replace('-', '')}C00000",
                                'underlying_ticker': ticker,
                                'expiration_date': exp_date,
                                'contract_type': 'call'
                            }
                            sample_put = {
                                'ticker': f"{ticker}{exp_date.replace('-', '')}P00000",
                                'underlying_ticker': ticker,
                                'expiration_date': exp_date,
                                'contract_type': 'put'
                            }
                            results.append(sample_call)
                            results.append(sample_put)
                        
                        return results
                    except:
                        pass
        except Exception as yf_error:
            print(f"Yahoo Finance options lookup failed: {str(yf_error)}")
            # Continue with Polygon as fallback
    
    # Check cache first if we have an expiration date
    cache_key = f"{ticker}_{expiration_date}"
    if expiration_date and cache_key in option_chain_cache:
        return option_chain_cache[cache_key]
    
    try:
        # Build the API endpoint
        if expiration_date:
            endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&expiration_date={expiration_date}&apiKey={POLYGON_API_KEY}"
        else:
            endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&apiKey={POLYGON_API_KEY}"
        
        # Use throttled API call
        response = throttled_api_call(endpoint, headers=get_headers())
            
        # If response indicates fallback or error, try Yahoo Finance
        if not response or response.status_code in [403, 429, 503]:
            print(f"Using Yahoo Finance fallback for {ticker} option chain")
            try:
                import yfinance as yf
                import pandas as pd
                
                stock = yf.Ticker(ticker)
                
                # If we need specific expiration
                if expiration_date:
                    try:
                        options = stock.option_chain(expiration_date)
                        # Convert Yahoo format to Polygon format
                        results = []
                        
                        # Process calls
                        for _, row in options.calls.iterrows():
                            results.append({
                                'ticker': f"{ticker}{expiration_date.replace('-', '')}C{int(row['strike']*1000)}",
                                'underlying_ticker': ticker,
                                'expiration_date': expiration_date,
                                'strike_price': float(row['strike']),
                                'contract_type': 'call',
                                'last_price': float(row['lastPrice']),
                                'volume': int(row['volume']),
                                'open_interest': int(row['openInterest'])
                            })
                        
                        # Process puts
                        for _, row in options.puts.iterrows():
                            results.append({
                                'ticker': f"{ticker}{expiration_date.replace('-', '')}P{int(row['strike']*1000)}",
                                'underlying_ticker': ticker,
                                'expiration_date': expiration_date,
                                'strike_price': float(row['strike']),
                                'contract_type': 'put',
                                'last_price': float(row['lastPrice']),
                                'volume': int(row['volume']),
                                'open_interest': int(row['openInterest'])
                            })
                        
                        # Cache the results
                        option_chain_cache[cache_key] = results
                        
                        return results
                    except Exception as e:
                        print(f"Error getting Yahoo chain for specific expiration: {str(e)}")
                else:
                    # If we just need available expirations
                    expirations = stock.options
                    if expirations:
                        # Get the first expiration's chain as an example
                        try:
                            options = stock.option_chain(expirations[0])
                            results = []
                            
                            # Process just a sample set to return format
                            for exp_date in expirations:
                                sample_call = {
                                    'ticker': f"{ticker}{exp_date.replace('-', '')}C00000",
                                    'underlying_ticker': ticker,
                                    'expiration_date': exp_date,
                                    'contract_type': 'call'
                                }
                                sample_put = {
                                    'ticker': f"{ticker}{exp_date.replace('-', '')}P00000",
                                    'underlying_ticker': ticker,
                                    'expiration_date': exp_date,
                                    'contract_type': 'put'
                                }
                                results.append(sample_call)
                                results.append(sample_put)
                            
                            return results
                        except:
                            pass
            except Exception as yf_error:
                print(f"Yahoo Finance options fallback also failed: {str(yf_error)}")
            return None  # Return None if both Polygon and Yahoo fail
        
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
        
        # Try Yahoo Finance as a fallback for any exception
        try:
            import yfinance as yf
            import pandas as pd
            print(f"Exception fallback to Yahoo Finance for {ticker} option chain")
            
            stock = yf.Ticker(ticker)
            
            if expiration_date:
                try:
                    options = stock.option_chain(expiration_date)
                    results = []
                    
                    # Process calls
                    for _, row in options.calls.iterrows():
                        results.append({
                            'ticker': f"{ticker}{expiration_date.replace('-', '')}C{int(row['strike']*1000)}",
                            'underlying_ticker': ticker,
                            'expiration_date': expiration_date,
                            'strike_price': float(row['strike']),
                            'contract_type': 'call',
                            'last_price': float(row['lastPrice']),
                            'volume': int(row['volume']),
                            'open_interest': int(row['openInterest'])
                        })
                    
                    # Process puts
                    for _, row in options.puts.iterrows():
                        results.append({
                            'ticker': f"{ticker}{expiration_date.replace('-', '')}P{int(row['strike']*1000)}",
                            'underlying_ticker': ticker,
                            'expiration_date': expiration_date,
                            'strike_price': float(row['strike']),
                            'contract_type': 'put',
                            'last_price': float(row['lastPrice']),
                            'volume': int(row['volume']),
                            'open_interest': int(row['openInterest'])
                        })
                    
                    # Cache the results
                    cache_key = f"{ticker}_{expiration_date}"
                    option_chain_cache[cache_key] = results
                    
                    return results
                except:
                    pass
            
            return None
        except Exception as yf_error:
            print(f"Yahoo Finance option chain fallback also failed: {str(yf_error)}")
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
            # Try Yahoo Finance as fallback
            try:
                import yfinance as yf
                print(f"Fallback to Yahoo Finance for {ticker} options chain")
                stock = yf.Ticker(ticker)
                options = stock.option_chain(expiration_date)
                
                if option_type == 'call':
                    chain_df = options.calls
                else:
                    chain_df = options.puts
                
                # Find closest strike
                closest_strike = chain_df.iloc[(chain_df['strike'] - float(strike_price)).abs().argsort()[:1]]
                if not closest_strike.empty:
                    return closest_strike['lastPrice'].values[0]
            except Exception as yf_error:
                print(f"Yahoo Finance options fallback failed: {str(yf_error)}")
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
            # Try Yahoo Finance as fallback for strike not found
            try:
                import yfinance as yf
                print(f"Fallback to Yahoo Finance for strike not found: {ticker} {strike_price} {option_type}")
                stock = yf.Ticker(ticker)
                options = stock.option_chain(expiration_date)
                
                if option_type == 'call':
                    chain_df = options.calls
                else:
                    chain_df = options.puts
                
                # Find closest strike
                closest_strike = chain_df.iloc[(chain_df['strike'] - float(strike_price)).abs().argsort()[:1]]
                if not closest_strike.empty:
                    return closest_strike['lastPrice'].values[0]
            except Exception as yf_error:
                print(f"Yahoo Finance options fallback failed: {str(yf_error)}")
            return None
        
        # Now get the latest price for this option
        endpoint = f"{BASE_URL}/v2/last/trade/{option_symbol}?apiKey={POLYGON_API_KEY}"
        response = throttled_api_call(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Error fetching option price: {response.status_code}")
            # If forbidden error (403), fallback to Yahoo Finance
            if response.status_code == 403:
                try:
                    import yfinance as yf
                    print(f"Fallback to Yahoo Finance for {ticker} {strike_price} {option_type} option price")
                    stock = yf.Ticker(ticker)
                    options = stock.option_chain(expiration_date)
                    
                    if option_type == 'call':
                        chain_df = options.calls
                    else:
                        chain_df = options.puts
                    
                    # Find closest strike
                    closest_match = chain_df.iloc[(chain_df['strike'] - float(strike_price)).abs().argsort()[:1]]
                    if not closest_match.empty:
                        return closest_match['lastPrice'].values[0]
                except Exception as yf_error:
                    print(f"Yahoo Finance option price fallback failed: {str(yf_error)}")
            return None
        
        data = response.json()
        result = data.get('results')
        
        if result:
            return result.get('p')  # 'p' is the price field
        
        return None
        
    except Exception as e:
        print(f"Error fetching option price: {str(e)}")
        
        # Try Yahoo Finance as a final fallback
        try:
            import yfinance as yf
            print(f"Exception fallback to Yahoo Finance for {ticker} {strike_price} {option_type}")
            stock = yf.Ticker(ticker)
            options = stock.option_chain(expiration_date)
            
            if option_type == 'call':
                chain_df = options.calls
            else:
                chain_df = options.puts
            
            # Find closest strike
            closest_match = chain_df.iloc[(chain_df['strike'] - float(strike_price)).abs().argsort()[:1]]
            if not closest_match.empty:
                return closest_match['lastPrice'].values[0]
        except Exception as yf_error:
            print(f"Yahoo Finance final fallback also failed: {str(yf_error)}")
            
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
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Get options for today's date
        chain = get_option_chain(ticker)
        
        if not chain:
            # Try to use yfinance for basic options activity
            try:
                import yfinance as yf
                import pandas as pd
                import numpy as np
                
                print(f"Fallback to Yahoo Finance for {ticker} unusual options activity")
                stock = yf.Ticker(ticker)
                
                # Get options expirations
                expirations = stock.options
                
                if not expirations or len(expirations) == 0:
                    return None
                
                # Use the closest expiration date
                exp_date = expirations[0]
                
                # Get option chain
                options = stock.option_chain(exp_date)
                
                # Process calls and puts
                calls_df = options.calls
                puts_df = options.puts
                
                # Combine unusual activity for both
                unusual_activity = []
                
                # For calls - find options with high volume relative to open interest
                if not calls_df.empty:
                    # Calculate volume to open interest ratio
                    calls_df['vol_oi_ratio'] = calls_df['volume'] / calls_df['openInterest'].replace(0, 1)
                    
                    # Sort by volume and take top options
                    top_calls = calls_df.sort_values('volume', ascending=False).head(3)
                    
                    # Add to unusual activity list
                    for _, row in top_calls.iterrows():
                        if row['volume'] > 20:  # Only include significant volume
                            premium = row['volume'] * row['lastPrice'] * 100  # Each contract is 100 shares
                            
                            if premium > 10000:  # Only include if premium is significant
                                unusual_activity.append({
                                    'contract': f"{ticker} {row['strike']} {exp_date} CALL",
                                    'volume': int(row['volume']),
                                    'avg_price': float(row['lastPrice']),
                                    'premium': premium,
                                    'sentiment': 'bullish'
                                })
                
                # For puts - similar analysis
                if not puts_df.empty:
                    # Calculate volume to open interest ratio
                    puts_df['vol_oi_ratio'] = puts_df['volume'] / puts_df['openInterest'].replace(0, 1)
                    
                    # Sort by volume and take top options
                    top_puts = puts_df.sort_values('volume', ascending=False).head(3)
                    
                    # Add to unusual activity list
                    for _, row in top_puts.iterrows():
                        if row['volume'] > 20:  # Only include significant volume
                            premium = row['volume'] * row['lastPrice'] * 100
                            
                            if premium > 10000:  # Only include if premium is significant
                                unusual_activity.append({
                                    'contract': f"{ticker} {row['strike']} {exp_date} PUT",
                                    'volume': int(row['volume']),
                                    'avg_price': float(row['lastPrice']),
                                    'premium': premium,
                                    'sentiment': 'bearish'
                                })
                
                # Sort by premium in descending order and return top 5
                if unusual_activity:
                    unusual_activity.sort(key=lambda x: x['premium'], reverse=True)
                    return unusual_activity[:5]
                    
            except Exception as yf_error:
                print(f"Yahoo Finance unusual activity fallback failed: {str(yf_error)}")
            
            return None
        
        # Get current stock price for context
        stock_price = get_current_price(ticker)
        
        # Track potential unusual activity
        unusual_activity = []
        forbidden_error_count = 0
        processed_options = 0
        
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
                    
                    # Get the actual transaction date if available
                    # We'll use our polygon_trades module to get the most significant trade
                    
                    trade_info = None
                    try:
                        trade_info = get_option_trade_data(option_symbol)
                    except Exception as e:
                        print(f"Error getting trade data for {option_symbol}: {str(e)}")
                        
                    # Create activity entry with or without transaction date
                    activity_entry = {
                        'contract': f"{ticker} {strike} {expiry} {contract_type.upper()}",
                        'volume': total_volume,
                        'avg_price': avg_price,
                        'premium': total_premium,
                        'sentiment': sentiment
                    }
                    
                    # Add transaction date if we have it
                    if trade_info and 'date' in trade_info:
                        activity_entry['transaction_date'] = trade_info['date']
                        
                    unusual_activity.append(activity_entry)
        
        # No fallback to Yahoo Finance - only using Polygon.io data as requested
        if forbidden_error_count > 5 and len(unusual_activity) == 0:
            print(f"Too many 403 errors for {ticker}, but not falling back to Yahoo Finance as requested")
            # Return empty list to indicate no unusual activity found
            return []
        
        # Sort by premium in descending order
        unusual_activity.sort(key=lambda x: x['premium'], reverse=True)
        
        # Take top 5 (if we have that many)
        return unusual_activity[:5]
        
    except Exception as e:
        print(f"Error fetching unusual activity for {ticker}: {str(e)}")
        # No fallback to Yahoo Finance - only using Polygon.io data as requested
        print(f"Not falling back to Yahoo Finance for {ticker} unusual options activity as requested")
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
    
    print(f"Using Polygon.io data for unusual activity summary for {ticker}")
    activity = get_unusual_options_activity(ticker)
    
    if not activity or len(activity) == 0:
        # No fallback to Yahoo Finance - only using Polygon.io data as requested
        print(f"No unusual options activity found for {ticker} in Polygon.io data, and not falling back to Yahoo Finance as requested")
        return f"📊 No significant unusual options activity detected for {ticker} in Polygon.io data.\n\nThis could indicate normal trading patterns or low options volume."
    
    # Determine overall sentiment
    bullish_count = sum(1 for item in activity if item.get('sentiment') == 'bullish')
    bearish_count = sum(1 for item in activity if item.get('sentiment') == 'bearish')
    
    if bullish_count > bearish_count:
        overall_sentiment = "bullish"
    elif bearish_count > bullish_count:
        overall_sentiment = "bearish"
    else:
        overall_sentiment = "neutral"
    
    # Create the summary with whale emojis
    summary = f"🐳 {ticker} Unusual Options Activity: {overall_sentiment.upper()} BIAS 🐳\n\n"
    
    for i, item in enumerate(activity):
        contract = item.get('contract', '')
        volume = item.get('volume', 0)
        premium = item.get('premium', 0)
        sentiment = item.get('sentiment', 'neutral')
        
        emoji = "🟢" if sentiment == 'bullish' else "🔴" if sentiment == 'bearish' else "⚪"
        
        summary += f"{emoji} {contract}:\n"
        
        # If we have a transaction date, include it
        if 'transaction_date' in item:
            summary += f"   {volume} contracts on {item['transaction_date']} (${premium:,.0f} premium)\n"
        else:
            summary += f"   {volume} contracts (${premium:,.0f} premium)\n"
    
    # Add overall analysis
    if overall_sentiment == "bullish":
        summary += "\nLarge traders are showing bullish sentiment with significant call buying."
    elif overall_sentiment == "bearish":
        summary += "\nLarge traders are showing bearish sentiment with significant put buying."
    else:
        summary += "\nMixed sentiment with balanced call and put activity."
    
    return summary