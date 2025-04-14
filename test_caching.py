import polygon_integration
import cache_module
import time
from datetime import datetime

def test_caching():
    """Test that caching for unusual options activity works properly"""
    
    print("\nTesting caching functionality:")
    
    # Make sure cache is empty
    if cache_module.get_cache_size() > 0:
        print(f"Starting with {cache_module.get_cache_size()} items in cache")
        cache_module.print_cache_contents()
    else:
        print("Starting with empty cache")
    
    # Test ticker
    test_ticker = "AAPL"
    print(f"\nChecking if {test_ticker} is in cache:")
    is_cached = cache_module.cache_contains(test_ticker)
    print(f"{test_ticker} in cache: {is_cached}")
    
    if not is_cached:
        print(f"\nMaking first request for {test_ticker}:")
        start_time = time.time()
        result = polygon_integration.get_unusual_options_activity(test_ticker)
        end_time = time.time()
        print(f"First request took {end_time - start_time:.2f} seconds")
        
        # Check that we now have it in cache
        print(f"\nAfter first request, checking if {test_ticker} is in cache:")
        is_cached = cache_module.cache_contains(test_ticker)
        print(f"{test_ticker} in cache: {is_cached}")
        
        # Make a second request which should use the cache
        print(f"\nMaking second request for {test_ticker} (should be faster):")
        start_time = time.time()
        result2 = polygon_integration.get_unusual_options_activity(test_ticker)
        end_time = time.time()
        print(f"Second request took {end_time - start_time:.2f} seconds")
        
        # Verify results
        if result == result2:
            print("Results match between first and second request")
        else:
            print("WARNING: Results differ between first and second request")
    else:
        print(f"{test_ticker} is already in cache, manually testing cached access:")
        cached_data, found = cache_module.get_from_cache(test_ticker)
        print(f"Cache retrieval successful: {found}")
        if found:
            print(f"Cache has {len(cached_data) if cached_data else 0} items for {test_ticker}")
    
    # Show cache state
    print("\nFinal cache contents:")
    cache_module.print_cache_contents()
    
if __name__ == "__main__":
    test_caching()