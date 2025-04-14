"""
Centralized cache module for OptionsWizard
All caches that need to persist across multiple function calls should be stored here
"""
from datetime import datetime

# Dictionary to store unusual options activity cache with timestamps
# Format: {ticker: {"timestamp": datetime, "data": activity_data}}
unusual_activity_cache = {}

def add_to_cache(ticker, data):
    """Add data to the unusual activity cache with current timestamp"""
    unusual_activity_cache[ticker] = {
        "timestamp": datetime.now(),
        "data": data
    }
    print(f"Added {ticker} to cache (will expire in 5 minutes)")
    
def get_from_cache(ticker):
    """
    Get data from the unusual activity cache if it exists and is not expired
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Tuple of (data, found) where found is a boolean indicating if the cache was used
    """
    if ticker in unusual_activity_cache:
        cache_entry = unusual_activity_cache[ticker]
        cache_age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
        
        # If cache is less than 5 minutes old (300 seconds), use it
        if cache_age < 300:
            print(f"Using cached unusual activity data for {ticker} ({cache_age:.1f} seconds old)")
            if cache_entry["data"]:
                print(f"Cache contains {len(cache_entry['data'])} items")
            else:
                print(f"Cache contains empty or None data")
            return cache_entry["data"], True
        else:
            print(f"Cached data for {ticker} is stale ({cache_age:.1f} seconds old), refreshing...")
            return None, False
    else:
        print(f"No cache entry found for {ticker}")
        return None, False
        
def cache_contains(ticker):
    """Check if ticker is in the cache"""
    return ticker in unusual_activity_cache
    
def get_cache_size():
    """Get the number of items in the cache"""
    return len(unusual_activity_cache)
    
def print_cache_contents():
    """Print contents of the cache for debugging"""
    print(f"Cache contains {len(unusual_activity_cache)} items:")
    for ticker, entry in unusual_activity_cache.items():
        age = (datetime.now() - entry["timestamp"]).total_seconds()
        data = entry["data"]
        data_desc = f"{len(data)} items" if isinstance(data, list) else "None"
        print(f"  {ticker}: {age:.1f} seconds old, {data_desc}")