"""
Centralized cache module for OptionsWizard
All caches that need to persist across multiple function calls should be stored here

The cache implements a market-hours aware expiration strategy:
- During market hours (9:30am-4:15pm ET, weekdays): 5-minute expiration
- Outside market hours and on weekends: no expiration until next market open
"""
from datetime import datetime, time, timedelta
import pytz

# Dictionary to store unusual options activity cache with timestamps
# Format: {ticker: {"timestamp": datetime, "data": activity_data}}
unusual_activity_cache = {}

def is_market_open():
    """
    Check if the US stock market is currently open
    
    Returns:
        bool: True if market is open (9:30am-4:15pm ET on weekdays), False otherwise
    """
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    
    # Check if it's a weekday (0 = Monday, 4 = Friday)
    if now.weekday() > 4:  # Saturday or Sunday
        return False
    
    # Check if within market hours (9:30am - 4:15pm ET)
    market_open = time(9, 30, 0)
    market_close = time(16, 15, 0)
    current_time = now.time()
    
    return market_open <= current_time <= market_close

def should_use_cached_data(cache_timestamp):
    """
    Determine if cached data should be used based on market hours
    
    Args:
        cache_timestamp: datetime when the cache entry was created
        
    Returns:
        bool: True if cached data should be used, False if it should be refreshed
    """
    # Convert timestamps to Eastern Time for market hour calculations
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    
    # If the cache entry has no timezone info, assume it's in local time and convert
    if cache_timestamp.tzinfo is None:
        cache_timestamp = eastern.localize(cache_timestamp)
    elif cache_timestamp.tzinfo != eastern:
        cache_timestamp = cache_timestamp.astimezone(eastern)
    
    # During market hours: 5-minute expiration
    if is_market_open():
        # In market hours, cache has a 5-minute expiration
        cache_age = (now - cache_timestamp).total_seconds()
        
        # For scenarios where we're explicitly testing market hours
        # Convert timestamps to same timezone for accurate comparison
        if now.tzinfo and cache_timestamp.tzinfo:
            now_time = now.astimezone(eastern)
            cache_time = cache_timestamp.astimezone(eastern)
            
            # If the timestamps are on same day and both during market hours
            if (now_time.date() == cache_time.date() and 
                time(9, 30) <= now_time.time() <= time(16, 15) and
                time(9, 30) <= cache_time.time() <= time(16, 15)):
                return cache_age < 300  # Less than 5 minutes old
            
        return cache_age < 300  # Standard 5-minute expiration
    
    # Get today's market close time
    today_market_close = eastern.localize(
        datetime.combine(now.date(), time(16, 15, 0))
    )
    
    # If we're after market close today
    if now.time() >= time(16, 15, 0) and now.weekday() <= 4:
        # Use cache if it was created after market close
        return cache_timestamp >= today_market_close
    
    # If today is Monday-Friday and we're before market open
    if now.weekday() <= 4 and now.time() < time(9, 30, 0):
        # Use cache if it was created after previous trading day's market close
        
        # Calculate previous trading day (handles weekends)
        if now.weekday() == 0:  # Monday
            prev_trading_day = now.date() - timedelta(days=3)  # Friday
        else:
            prev_trading_day = now.date() - timedelta(days=1)
        
        prev_market_close = eastern.localize(
            datetime.combine(prev_trading_day, time(16, 15, 0))
        )
        
        return cache_timestamp >= prev_market_close
    
    # If it's weekend
    if now.weekday() >= 5:  # Saturday or Sunday
        # Calculate last Friday
        days_since_friday = (now.weekday() - 4) % 7
        last_friday = now.date() - timedelta(days=days_since_friday)
        
        # Friday market close time
        friday_close = eastern.localize(
            datetime.combine(last_friday, time(16, 15, 0))
        )
        
        # Check if the cache entry was created after market close on Friday
        if cache_timestamp.date() == last_friday and cache_timestamp.time() >= time(16, 15, 0):
            return True
        
        # For entries created on Saturday or Sunday, they're valid if created during the weekend
        if cache_timestamp.weekday() >= 5:
            return True
            
        # Otherwise the entry is too old (from before Friday close)
        return False
    
    # Should not reach here during normal operation
    # Fallback to 5-minute expiration
    cache_age = (now - cache_timestamp).total_seconds()
    return cache_age < 300

def add_to_cache(ticker, data):
    """Add data to the unusual activity cache with current timestamp"""
    timestamp = datetime.now()
    unusual_activity_cache[ticker] = {
        "timestamp": timestamp,
        "data": data
    }
    
    if is_market_open():
        print(f"Added {ticker} to cache (will expire in 5 minutes)")
    else:
        print(f"Added {ticker} to cache (will persist until next market open)")
    
def get_from_cache(ticker):
    """
    Get data from the unusual activity cache if it exists and is not expired
    Uses market-hours aware caching strategy:
    - During market hours: 5-minute expiration
    - Outside market hours: cache persists until next market open
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Tuple of (data, found) where found is a boolean indicating if the cache was used
    """
    if ticker in unusual_activity_cache:
        cache_entry = unusual_activity_cache[ticker]
        cache_timestamp = cache_entry["timestamp"]
        cache_age = (datetime.now() - cache_timestamp).total_seconds()
        
        # Check if we should use the cached data based on market hours
        if should_use_cached_data(cache_timestamp):
            market_status = "open" if is_market_open() else "closed"
            print(f"Using cached unusual activity data for {ticker} ({cache_age:.1f} seconds old, market {market_status})")
            if cache_entry["data"]:
                print(f"Cache contains {len(cache_entry['data'])} items")
            else:
                print(f"Cache contains empty or None data")
            return cache_entry["data"], True
        else:
            if is_market_open():
                print(f"Cached data for {ticker} is stale ({cache_age:.1f} seconds old), refreshing...")
            else:
                print(f"Cached data for {ticker} is from before market close, refreshing...")
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
    market_status = "open" if is_market_open() else "closed"
    print(f"Cache contains {len(unusual_activity_cache)} items (market is {market_status}):")
    for ticker, entry in unusual_activity_cache.items():
        timestamp = entry["timestamp"]
        age = (datetime.now() - timestamp).total_seconds()
        data = entry["data"]
        data_desc = f"{len(data)} items" if isinstance(data, list) else "None"
        valid = should_use_cached_data(timestamp)
        status = "VALID" if valid else "EXPIRED"
        print(f"  {ticker}: {age:.1f} seconds old, {data_desc} - {status}")