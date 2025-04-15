"""
Test the parallel processing implementation for options analysis
"""

import os
import time
from polygon_integration import get_headers, get_unusual_options_activity, get_current_price
import cache_module

def test_parallel_processing(force_refresh=True):
    # Clear cache to ensure a fresh run
    if force_refresh:
        print("Forcing fresh API call by clearing cache...")
        # Remove the specific ticker from cache to force a fresh API call
        if 'SPY' in cache_module.unusual_activity_cache:
            del cache_module.unusual_activity_cache['SPY']
        cache_module.save_cache()
    
    # Test with SPY (S&P 500 ETF) which has many options
    ticker = "SPY"
    
    # Time the operation
    start_time = time.time()
    print(f"Testing unusual options activity for {ticker}...")
    
    # Get the data
    result = get_unusual_options_activity(ticker)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print results
    if result:
        if isinstance(result, dict) and 'unusual_options' in result:
            options_count = result.get('all_options_analyzed', 0)
            unusual_count = len(result.get('unusual_options', []))
            bullish = result.get('total_bullish_count', 0)
            bearish = result.get('total_bearish_count', 0)
            
            print(f"Processed {options_count} options in {duration:.2f} seconds")
            print(f"Found {unusual_count} unusual options")
            
            if bullish + bearish > 0:
                bullish_pct = (bullish / (bullish + bearish)) * 100
                bearish_pct = (bearish / (bullish + bearish)) * 100
                print(f"Overall flow: {bullish_pct:.1f}% bullish, {bearish_pct:.1f}% bearish")
            
            # Display the top 5 unusual options
            print("\nTop unusual options:")
            for idx, option in enumerate(result.get('unusual_options', [])[:5]):
                print(f"{idx+1}. {option.get('contract', 'Unknown')} - Score: {option.get('unusualness_score', 0)}")
                if 'transaction_date' in option:
                    print(f"   Transaction date: {option.get('transaction_date')}")
        else:
            print(f"Old-format result: Found {len(result)} unusual options")
    else:
        print("No results found")
    
    print(f"Total time: {duration:.2f} seconds")
    
    # Test that caching works by running it again (should be much faster)
    print("\nTesting with cached data...")
    start_time = time.time()
    cache_result = get_unusual_options_activity(ticker)
    cache_duration = time.time() - start_time
    
    print(f"Cached result fetched in {cache_duration:.2f} seconds")
    print(f"Speed improvement: {duration/cache_duration:.1f}x faster with cache")
    
    return result

if __name__ == "__main__":
    test_parallel_processing()