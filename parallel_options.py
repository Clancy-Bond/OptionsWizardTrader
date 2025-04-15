"""
Parallel processing module for options analysis
This module implements concurrent processing for options data
to improve performance when analyzing many options simultaneously.
"""

import concurrent.futures
from functools import partial

# We'll need these imports from polygon_integration.py
# They're included here to make the file self-contained
import cache_module
import json
import os
import re
import time
from datetime import datetime, timedelta
import requests
from polygon_trades import get_option_trade_data

# Configuration
MAX_WORKERS = 8  # Adjust based on your CPU cores
BATCH_SIZE = None  # None means auto-determine based on number of options

# Function to process a single option
def process_single_option(option, stock_price, headers, forbidden_error_count=0, all_options=None):
    """
    Process a single option to determine if it has unusual activity
    This function is designed to be run in parallel by the ThreadPoolExecutor
    
    Args:
        option: The option data to analyze
        stock_price: Current price of the underlying stock
        headers: API request headers
        forbidden_error_count: Counter for 403 errors (shared across threads)
        all_options: List to collect ALL options analyzed (shared across threads)
        
    Returns:
        Tuple of (option_data, unusualness_score, is_unusual, sentiment)
    """
    if not all_options:
        all_options = []
        
    try:
        option_symbol = option.get('ticker')
        ticker = option.get('underlying_ticker', '').upper()
        strike = option.get('strike_price')
        expiry = option.get('expiration_date')
        contract_type = option.get('contract_type', '').lower()
        
        # These URLs and functions would need to come from polygon_integration.py
        POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY', '')
        BASE_URL = "https://api.polygon.io"
        
        # Get trades for this option
        endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=50&order=desc&apiKey={POLYGON_API_KEY}"
        
        # Make the API call with proper headers
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code != 200:
            return None, 0, False, None
            
        data = response.json()
        trades = data.get('results', [])
        
        # Skip if no trades
        if not trades:
            return None, 0, False, None
            
        # This would be imported from polygon_integration.py in practice
        def calculate_unusualness_score(option, trades, stock_price):
            # Placeholder for the actual function
            # In practice, you'd import this from polygon_integration.py
            
            # Simulate a score between 0-60
            volume = sum(t.get('size', 0) for t in trades)
            avg_price = sum(t.get('price', 0) * t.get('size', 0) for t in trades) / volume if volume > 0 else 0
            score = min(60, int(volume / 10) + int(avg_price * 10))
            
            return score, {"volume": volume, "price": avg_price}
        
        # Calculate unusualness score
        unusualness_score, score_breakdown = calculate_unusualness_score(option, trades, stock_price)
        
        # Calculate metrics for the activity
        total_volume = sum(t.get('size', 0) for t in trades)
        avg_price = sum(t.get('price', 0) * t.get('size', 0) for t in trades) / total_volume if total_volume > 0 else 0
        total_premium = total_volume * 100 * avg_price  # Each contract is 100 shares
        
        # Determine sentiment based on option type
        sentiment = None
        if contract_type == 'call':
            sentiment = 'bullish'
        elif contract_type == 'put':
            sentiment = 'bearish'
        
        # Get the actual transaction date if available
        trade_info = None
        try:
            trade_info = get_option_trade_data(option_symbol)
        except Exception as e:
            print(f"Error getting trade data for {option_symbol}: {str(e)}")
        
        # Create option data entry
        option_entry = {
            'contract': f"{ticker} {strike} {expiry} {contract_type.upper()}",
            'volume': total_volume,
            'avg_price': avg_price,
            'premium': total_premium,
            'sentiment': sentiment,
            'unusualness_score': unusualness_score,
            'score_breakdown': score_breakdown
        }
        
        # Add detailed transaction information if we have it
        if trade_info:
            if 'date' in trade_info:
                option_entry['transaction_date'] = trade_info['date']
            
            # Include exchange information
            if 'exchange' in trade_info:
                option_entry['exchange'] = trade_info['exchange']
                
            # Include exact timestamp if available
            if 'timestamp' in trade_info:
                option_entry['timestamp'] = trade_info['timestamp']
                
            # Include human-readable timestamp if available
            if 'timestamp_human' in trade_info:
                option_entry['timestamp_human'] = trade_info['timestamp_human']
        
        # Make sure volume is always available
        if 'volume' not in option_entry:
            option_entry['volume'] = 0
            
        # If we have trade info, use the actual trade size for volume calculation
        if trade_info and 'size' in trade_info and trade_info['size'] > 0:
            option_entry['contract_volume'] = trade_info['size']
        else:
            # Fallback to 1 (minimum) if no significant trades found
            option_entry['contract_volume'] = 1
        
        # Is this option unusual enough to report?
        is_unusual = unusualness_score >= 30
        
        return option_entry, unusualness_score, is_unusual, sentiment
        
    except Exception as e:
        print(f"Error processing option {option.get('ticker', 'unknown')}: {str(e)}")
        return None, 0, False, None

def analyze_options_in_parallel(near_money_options, stock_price, headers, max_workers=MAX_WORKERS):
    """
    Analyze options in parallel using a thread pool
    
    Args:
        near_money_options: List of options to analyze
        stock_price: Current price of the underlying stock
        headers: API request headers
        max_workers: Maximum number of parallel worker threads
        
    Returns:
        Dictionary with results including unusual options, sentiment counts, etc.
    """
    # Lists to collect results
    all_options = []
    unusual_activity = []
    
    # Determine optimal number of workers
    # Adjust max_workers based on the number of options to process
    worker_count = min(max_workers, len(near_money_options))
    
    print(f"Found {len(near_money_options)} near-the-money options to analyze")
    print(f"Using {worker_count} parallel workers for analysis")
    
    # Prepare the partial function with fixed parameters
    process_func = partial(process_single_option, stock_price=stock_price, headers=headers)
    
    # Create a thread pool and process options in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        # Submit all jobs to the executor
        future_to_option = {executor.submit(process_func, option): option for option in near_money_options}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_option):
            option = future_to_option[future]
            option_symbol = option.get('ticker', 'unknown')
            
            try:
                option_entry, unusualness_score, is_unusual, sentiment = future.result()
                
                if option_entry:
                    # Add to the list of all options analyzed
                    all_options.append(option_entry)
                    
                    # If unusual enough, add to unusual activity list
                    if is_unusual:
                        unusual_activity.append(option_entry.copy())
                        
                    # Print progress info occasionally
                    if len(all_options) % 20 == 0 or is_unusual:
                        print(f"Processed {len(all_options)}/{len(near_money_options)} options. Latest: {option_symbol} (Score: {unusualness_score})")
                
            except Exception as e:
                print(f"Error processing results for {option_symbol}: {str(e)}")
    
    # Calculate sentiment counts from ALL options analyzed (not just unusual ones)
    # Use contract volume to weight the sentiment counts
    all_bullish_count = sum(item.get('contract_volume', 1) for item in all_options if item.get('sentiment') == 'bullish')
    all_bearish_count = sum(item.get('contract_volume', 1) for item in all_options if item.get('sentiment') == 'bearish')
    
    # Print detailed breakdown of all options analyzed
    print(f"COMPLETE BREAKDOWN OF ALL OPTIONS: {len(all_options)} total options analyzed")
    all_total_contracts = all_bullish_count + all_bearish_count
    
    # Calculate volume-weighted percentages
    bullish_pct = (all_bullish_count / all_total_contracts * 100) if all_total_contracts > 0 else 0
    bearish_pct = (all_bearish_count / all_total_contracts * 100) if all_total_contracts > 0 else 0
    print(f"Volume-weighted sentiment: {all_bullish_count} bullish contracts ({bullish_pct:.1f}%) / {all_bearish_count} bearish contracts ({bearish_pct:.1f}%)")
    
    # Also print breakdown of just the unusual options for comparison
    unusual_bullish = sum(1 for item in unusual_activity if item.get('sentiment') == 'bullish')
    unusual_bearish = sum(1 for item in unusual_activity if item.get('sentiment') == 'bearish')
    print(f"UNUSUAL OPTIONS ONLY: {len(unusual_activity)} unusual options found")
    if len(unusual_activity) > 0:
        print(f"Unusual options sentiment: {unusual_bullish} bullish ({unusual_bullish/len(unusual_activity)*100:.1f}%) / {unusual_bearish} bearish ({unusual_bearish/len(unusual_activity)*100:.1f}%)")
    
    # Sort by unusualness score in descending order, with premium as a secondary factor
    unusual_activity.sort(key=lambda x: (x.get('unusualness_score', 0), x.get('premium', 0)), reverse=True)
    
    # Display top 10 unusual options
    if len(unusual_activity) > 0:
        print("TOP 10 MOST UNUSUAL OPTIONS:")
        for idx, item in enumerate(unusual_activity[:10]):
            print(f"  {idx+1}. {item.get('contract', 'Unknown')} - Score: {item.get('unusualness_score', 0)} - Sentiment: {item.get('sentiment', 'Unknown')} - Premium: ${item.get('premium', 0)/1000000:.2f}M")
    
    # Take top 5 (if we have that many)
    result = unusual_activity[:5]
    
    # Add the overall sentiment counts to the result (using ALL options, not just unusual ones)
    result_with_metadata = {
        'unusual_options': result,
        'total_bullish_count': all_bullish_count,
        'total_bearish_count': all_bearish_count,
        'all_options_analyzed': len(all_options)
    }
    
    return result_with_metadata