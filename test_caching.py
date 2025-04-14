import time
import polygon_integration

def test_caching():
    """Test that caching for unusual options activity works properly"""
    print("Cache before first call:", len(polygon_integration.unusual_activity_cache))
    
    # First call should hit the API
    print("\nFirst API call for AAPL...")
    start_time = time.time()
    result1 = polygon_integration.get_unusual_options_activity('AAPL')
    first_call_time = time.time() - start_time
    print(f"First call execution time: {first_call_time:.2f} seconds")
    print("Cache after first call:", len(polygon_integration.unusual_activity_cache))
    
    # Second call should use the cache
    print("\nSecond API call for AAPL (should use cache)...")
    start_time = time.time()
    result2 = polygon_integration.get_unusual_options_activity('AAPL')
    second_call_time = time.time() - start_time
    print(f"Second call execution time: {second_call_time:.2f} seconds")
    print(f"Speedup factor: {first_call_time / second_call_time:.1f}x faster")
    
    # Try a different ticker
    print("\nAPI call for different ticker (SPY)...")
    start_time = time.time()
    result3 = polygon_integration.get_unusual_options_activity('SPY')
    third_call_time = time.time() - start_time
    print(f"SPY call execution time: {third_call_time:.2f} seconds")
    
    # Show final cache state
    print("\nFinal cache contents:", polygon_integration.unusual_activity_cache.keys())

if __name__ == "__main__":
    test_caching()