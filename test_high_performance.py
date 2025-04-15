import os
import time
import unusual_activity as ua
import cache_module

def test_high_performance_mode():
    """
    Test both regular and high-performance modes for various tickers
    to measure performance differences.
    """
    # List of tickers to test (mix of high volume and regular) - keep short for test
    tickers = ['AAPL', 'TSLA']
    
    # Clear cache for these tickers to ensure accurate timing
    for ticker in tickers:
        cache_module.remove_from_cache(ticker)
    
    print("\n==== Testing Regular Mode ====")
    regular_times = {}
    for ticker in tickers:
        print(f"\nTesting {ticker} in regular mode...")
        start_time = time.time()
        # Clear any high-performance flag
        if 'HIGH_PERFORMANCE_MODE' in os.environ:
            del os.environ['HIGH_PERFORMANCE_MODE']
        summary = ua.get_simplified_unusual_activity_summary(ticker, high_performance=False)
        elapsed = time.time() - start_time
        regular_times[ticker] = elapsed
        print(f"{ticker}: Completed in {elapsed:.2f} seconds")
        
    print("\n==== Testing High-Performance Mode ====")
    hp_times = {}
    for ticker in tickers:
        print(f"\nTesting {ticker} in high-performance mode...")
        start_time = time.time()
        summary = ua.get_simplified_unusual_activity_summary(ticker, high_performance=True)
        elapsed = time.time() - start_time
        hp_times[ticker] = elapsed
        print(f"{ticker}: Completed in {elapsed:.2f} seconds")
        
    # Print comparison
    print("\n==== Performance Comparison ====")
    print("Ticker\tRegular\tHigh-Perf\tImprovement")
    print("--------------------------------------")
    for ticker in tickers:
        regular = regular_times.get(ticker, 0)
        hp = hp_times.get(ticker, 0)
        if regular > 0:
            improvement = (regular - hp) / regular * 100
            print(f"{ticker}\t{regular:.2f}s\t{hp:.2f}s\t{improvement:.1f}%")
        else:
            print(f"{ticker}\t{regular:.2f}s\t{hp:.2f}s\tN/A")

if __name__ == "__main__":
    test_high_performance_mode()