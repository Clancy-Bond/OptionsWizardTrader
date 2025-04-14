import polygon_integration
import time
from datetime import datetime

def test_basic_caching():
    """Basic test of caching functionality"""
    print("Cache before anything:", polygon_integration.unusual_activity_cache)
    
    # Create a mock entry in the cache
    ticker = "TEST"
    polygon_integration.unusual_activity_cache[ticker] = {
        "timestamp": datetime.now(),  # Use datetime object, not timestamp
        "data": ["mock data"]
    }
    
    print("\nCache after adding mock entry:", polygon_integration.unusual_activity_cache)
    
    # Check if get_unusual_options_activity would use the cache
    if ticker in polygon_integration.unusual_activity_cache:
        cache_entry = polygon_integration.unusual_activity_cache[ticker]
        cache_age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
        if cache_age < 300:  # 5 minutes in seconds
            print(f"Cache for {ticker} would be used (age: {cache_age:.1f} seconds)")
        else:
            print(f"Cache for {ticker} would be refreshed (age: {cache_age:.1f} seconds)")
    
    # Now try getting it - we'll create a minimal mock function to test this
    original_func = polygon_integration.get_option_chain
    try:
        # Replace the actual function with a mock
        def mock_option_chain(ticker):
            print(f"Mock option chain called for {ticker}")
            return []
        
        polygon_integration.get_option_chain = mock_option_chain
        
        print(f"\nGet unusual activity for {ticker} (should use cache)...")
        result = polygon_integration.get_unusual_options_activity(ticker)
        print(f"Result: {result}")
        
        # Try a different ticker (should try to call the API)
        different_ticker = "DIFFERENT"
        print(f"\nGet unusual activity for {different_ticker} (should try API)...")
        result = polygon_integration.get_unusual_options_activity(different_ticker)
        print(f"Result: {result}")
        
    finally:
        # Restore the original function
        polygon_integration.get_option_chain = original_func
    
    print("\nFinal cache state:", polygon_integration.unusual_activity_cache)

if __name__ == "__main__":
    test_basic_caching()