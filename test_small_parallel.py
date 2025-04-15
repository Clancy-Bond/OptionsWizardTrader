"""
Test the parallel processing implementation with a small sample of options
This script tests the parallel options analysis with just a few options
to verify that the implementation works correctly without timing out
"""

import time
import concurrent.futures
from polygon_integration import get_headers, get_current_price, throttled_api_call
from parallel_options import process_single_option, MAX_WORKERS
import json

def test_small_sample():
    """Test parallel processing with a very small sample set of 4 options"""
    print("Testing parallel processing with a small sample set...")
    ticker = "AAPL"
    
    # Get stock price
    stock_price = get_current_price(ticker)
    if not stock_price:
        stock_price = 175.0  # Fallback price if API call fails
        print(f"Using fallback price for {ticker}: ${stock_price}")
    else:
        print(f"Current price for {ticker}: ${stock_price}")
        
    headers = get_headers()
    
    # Create a small sample of options to test with
    sample_options = [
        {"ticker": "O:AAPL250417C00170000", "contract_type": "call", "strike_price": 170, "expiration_date": "2025-04-17"},
        {"ticker": "O:AAPL250417P00170000", "contract_type": "put", "strike_price": 170, "expiration_date": "2025-04-17"},
        {"ticker": "O:AAPL250417C00180000", "contract_type": "call", "strike_price": 180, "expiration_date": "2025-04-17"},
        {"ticker": "O:AAPL250417P00180000", "contract_type": "put", "strike_price": 180, "expiration_date": "2025-04-17"}
    ]
    
    start_time = time.time()
    print(f"Starting parallel processing with {len(sample_options)} options...")
    
    # Create a thread pool and process options in parallel
    print(f"Using {MAX_WORKERS} parallel workers for analysis")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all option analysis tasks to the thread pool
        future_to_option = {
            executor.submit(process_single_option, option, stock_price, headers, ticker): option 
            for option in sample_options
        }
        
        # Process results as they complete
        for i, future in enumerate(concurrent.futures.as_completed(future_to_option)):
            option = future_to_option[future]
            try:
                option_data, unusualness_score, is_unusual, sentiment = future.result()
                results.append({
                    'contract': option['ticker'],
                    'unusualness_score': unusualness_score,
                    'is_unusual': is_unusual,
                    'sentiment': sentiment
                })
                print(f"Processed {i+1}/{len(sample_options)}: {option['ticker']} - Score: {unusualness_score}")
            except Exception as e:
                print(f"Error processing {option['contract']}: {str(e)}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print results
    print(f"\nProcessed {len(sample_options)} options in {duration:.2f} seconds")
    print("\nResults:")
    for i, result in enumerate(sorted(results, key=lambda x: x['unusualness_score'], reverse=True)):
        print(f"{i+1}. {result['contract']} - Score: {result['unusualness_score']} - {result['sentiment']}")
    
    # Print timing information
    print(f"\nTotal parallel processing time: {duration:.2f} seconds")
    print(f"Average time per option: {duration/len(sample_options):.2f} seconds")
    
    # Calculate thread efficiency
    theoretical_serial_time = duration * len(sample_options) / MAX_WORKERS
    if theoretical_serial_time > 0:
        speedup = theoretical_serial_time / duration
        print(f"Theoretical speedup vs. serial processing: {speedup:.1f}x")
    
    return results

if __name__ == "__main__":
    test_small_sample()