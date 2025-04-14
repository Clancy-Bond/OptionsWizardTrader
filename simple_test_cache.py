import datetime
import cache_module
from polygon_integration import get_unusual_options_activity, extract_strike_from_symbol

def test_basic_caching():
    """Basic test of caching functionality"""
    
    test_ticker = "AAPL"
    
    print(f"Testing cache for {test_ticker}")
    
    # Check if ticker is already in cache
    if cache_module.cache_contains(test_ticker):
        print(f"{test_ticker} already in cache")
        cached_data, found = cache_module.get_from_cache(test_ticker)
        print(f"Found in cache: {found}")
        if found:
            print(f"Cache contains {len(cached_data) if cached_data else 0} items")
    else:
        print(f"{test_ticker} not in cache, making API call")
    
    # Make first API call (or use cache if available)
    unusual_activity = get_unusual_options_activity(test_ticker)
    
    # Check cache status after first call
    if cache_module.cache_contains(test_ticker):
        print(f"{test_ticker} successfully cached after first call")
    else:
        print(f"ERROR: {test_ticker} not cached after first call")
    
    # Test strike extraction
    symbol = "O:AAPL250417C00195000"
    strike = extract_strike_from_symbol(symbol)
    print(f"Extracted strike from {symbol}: {strike}")
    
    # Test cache expiration
    print("\nTesting cache expiration...")
    print("Cache should expire items after 5 minutes")
    print("Current cache contents:")
    cache_module.print_cache_contents()

if __name__ == "__main__":
    test_basic_caching()