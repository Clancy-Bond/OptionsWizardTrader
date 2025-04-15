"""
Parallel processing module for options analysis
This module implements concurrent processing for options data
to improve performance when analyzing many options simultaneously.
"""

import concurrent.futures
from functools import partial
import threading

# We'll need these imports from polygon_integration.py
# They're included here to make the file self-contained
import cache_module
import json
import os
import re
import time
from datetime import datetime, timedelta, date
import requests
from polygon_trades import get_option_trade_data, format_timestamp

# Configuration
MAX_WORKERS = 8  # Adjust based on your CPU cores
BATCH_SIZE = None  # None means auto-determine based on number of options
BASE_URL = "https://api.polygon.io"
POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY', '')

# Thread-local storage for error tracking
# This helps us track errors across multiple worker threads
thread_local = threading.local()

# Create thread-safe counters for tracking API errors
error_lock = threading.Lock()
forbidden_errors = 0

def filter_trades_by_date(trades, min_date=None):
    """
    Filter trades to only include those after the specified date
    
    Args:
        trades: List of trade objects from Polygon API
        min_date: Minimum date string in YYYY-MM-DD format (e.g., '2025-04-07')
        
    Returns:
        Filtered list of trades
    """
    if not min_date:
        return trades
        
    try:
        # Convert min_date string to datetime object
        min_date_obj = datetime.strptime(min_date, '%Y-%m-%d').date()
        
        # Filter trades by timestamp
        filtered_trades = []
        for trade in trades:
            # Get timestamp from trade
            timestamp = trade.get('participant_timestamp') or trade.get('sip_timestamp')
            if timestamp:
                # Convert nanoseconds to datetime
                trade_date = datetime.fromtimestamp(timestamp / 1e9).date()
                # Include only trades on or after min_date
                if trade_date >= min_date_obj:
                    filtered_trades.append(trade)
        
        print(f"Filtered {len(trades)} trades to {len(filtered_trades)} trades after {min_date}")
        return filtered_trades
    except Exception as e:
        print(f"Error filtering trades by date: {str(e)}")
        return trades  # Return original trades if there's an error

# Function to process a single option
def process_single_option(option, stock_price, headers, ticker):
    """
    Process a single option to determine if it has unusual activity
    This function is designed to be run in parallel by the ThreadPoolExecutor
    
    Args:
        option: The option data to analyze
        stock_price: Current price of the underlying stock
        headers: API request headers
        ticker: The underlying stock ticker symbol
        
    Returns:
        Tuple of (option_data, unusualness_score, is_unusual, sentiment)
    """
    global forbidden_errors
    
    try:
        option_symbol = option.get('ticker')
        strike = option.get('strike_price')
        expiry = option.get('expiration_date')
        contract_type = option.get('contract_type', '').lower()
        
        # Print progress info
        print(f"Processing {option_symbol} ({contract_type.upper()} {strike})")
        
        # Get trades for this option
        endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=50&order=desc&apiKey={POLYGON_API_KEY}"
        
        # Make the API call with proper headers
        response = requests.get(endpoint, headers=headers)
        
        # Handle API error responses
        if response.status_code != 200:
            if response.status_code == 403:
                with error_lock:
                    forbidden_errors += 1
                if forbidden_errors > 5:
                    print(f"Multiple 403 errors for {option_symbol}, API access issue detected")
            return None, 0, False, None
            
        data = response.json()
        trades = data.get('results', [])
        
        # Print number of trades found
        print(f"Found {len(trades)} trades for {option_symbol}")
        
        # Skip if no trades
        if not trades:
            return None, 0, False, None
            
        # Filter trades by date (only include trades after April 7th, 2025)
        min_date = "2025-04-07"
        trades = filter_trades_by_date(trades, min_date)
        
        # Skip if no trades remain after filtering
        if not trades:
            print(f"No trades found after {min_date} for {option_symbol}")
            return None, 0, False, None
        
        # Get the scoring function - defined at module level to avoid circular imports
        # as we're importing it locally inside the function
        try:
            # First try importing directly
            from polygon_integration import calculate_unusualness_score
        except ImportError:
            # If that fails, define a simple scoring function as fallback
            print("Warning: Could not import calculate_unusualness_score, using simple fallback")
            def calculate_unusualness_score(option, trades, stock_price):
                """Fallback scoring function mimicking the main implementation"""
                score = 0
                score_breakdown = {}
                
                # Extract basic option information
                strike = option.get('strike_price', 0)
                contract_type = option.get('contract_type', '').lower()
                expiration_date = option.get('expiration_date', '')
                open_interest = option.get('open_interest', 0)
                
                # If we have no trades or basic data is missing, return 0 score
                if not trades or not strike or not contract_type or not expiration_date:
                    return 0, {}
                
                # 1. Large Block Trades (0-25 points)
                large_trades = [t for t in trades if t.get('size', 0) >= 10]
                largest_trade_size = max([t.get('size', 0) for t in trades], default=0)
                
                # Score based on largest single trade size
                block_trade_score = 0
                if largest_trade_size >= 100:
                    block_trade_score = 25  # Very large block
                elif largest_trade_size >= 50:
                    block_trade_score = 20
                elif largest_trade_size >= 20:
                    block_trade_score = 15
                elif largest_trade_size >= 10:
                    block_trade_score = 10
                elif largest_trade_size >= 5:
                    block_trade_score = 5
                
                score += block_trade_score
                score_breakdown['block_trade'] = block_trade_score
                
                # 2. Volume to Open Interest Ratio (0-20 points)
                total_volume = sum(t.get('size', 0) for t in trades)
                
                vol_oi_score = 0
                if open_interest > 0:
                    vol_oi_ratio = total_volume / open_interest
                    if vol_oi_ratio >= 1.0:  # Volume exceeds open interest
                        vol_oi_score = 20
                    elif vol_oi_ratio >= 0.5:
                        vol_oi_score = 15
                    elif vol_oi_ratio >= 0.3:
                        vol_oi_score = 10
                    elif vol_oi_ratio >= 0.2:
                        vol_oi_score = 5
                    elif vol_oi_ratio >= 0.1:
                        vol_oi_score = 3
                elif total_volume > 20:
                    # Even without open interest data, high absolute volume is notable
                    vol_oi_score = 10
                
                score += vol_oi_score
                score_breakdown['volume_to_oi'] = vol_oi_score
                
                # NEW: Open Interest Size (0-15 points)
                oi_size_score = 0
                if open_interest >= 1000:
                    oi_size_score = 15  # Very high open interest
                elif open_interest >= 500:
                    oi_size_score = 10
                elif open_interest >= 100:
                    oi_size_score = 5
                
                score += oi_size_score
                score_breakdown['open_interest_size'] = oi_size_score
                
                # 3. Strike Price Distance (0-15 points)
                if stock_price > 0:
                    strike_distance = abs(strike - stock_price) / stock_price
                    
                    strike_score = 0
                    if strike_distance >= 0.2:  # 20%+ OTM
                        strike_score = 15
                    elif strike_distance >= 0.1:  # 10-20% OTM
                        strike_score = 10
                    elif strike_distance >= 0.05:  # 5-10% OTM
                        strike_score = 5
                    
                    score += strike_score
                    score_breakdown['strike_distance'] = strike_score
                
                # 4. Premium Size (0-20 points)
                avg_price = sum(t.get('price', 0) * t.get('size', 0) for t in trades) / total_volume if total_volume > 0 else 0
                total_premium = total_volume * 100 * avg_price  # Each contract is 100 shares
                
                premium_score = 0
                if total_premium >= 1000000:  # $1M+
                    premium_score = 20
                elif total_premium >= 500000:  # $500K+
                    premium_score = 15
                elif total_premium >= 100000:  # $100K+
                    premium_score = 10
                elif total_premium >= 50000:  # $50K+
                    premium_score = 5
                
                score += premium_score
                score_breakdown['premium_size'] = premium_score
                
                # Calculate total score (max 100)
                final_score = min(score, 100)
                
                # Add basic trade information for reference
                score_breakdown['total_volume'] = total_volume
                score_breakdown['total_premium'] = total_premium
                score_breakdown['largest_trade'] = largest_trade_size
                if open_interest > 0:
                    score_breakdown['vol_oi_ratio'] = round(total_volume / open_interest, 2)
                
                return final_score, score_breakdown
        
        # Calculate unusualness score
        unusualness_score, score_breakdown = calculate_unusualness_score(option, trades, stock_price)
        print(f"Option {option_symbol} received unusualness score: {unusualness_score}")
        
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
            # Use the same date filter as we did for the options
            min_date = "2025-04-07"
            trade_info = get_option_trade_data(option_symbol, min_size=5, min_date=min_date)
            if trade_info:
                print(f"Found {'significant' if trade_info.get('size', 0) > 0 else 'recent'} trade with size {trade_info.get('size', 0)} for {option_symbol}")
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

def analyze_options_in_parallel(near_money_options, stock_price, headers, ticker, max_workers=MAX_WORKERS):
    """
    Analyze options in parallel using a thread pool
    
    Args:
        near_money_options: List of options to analyze
        stock_price: Current price of the underlying stock
        headers: API request headers
        ticker: The stock ticker symbol
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
    process_func = partial(process_single_option, stock_price=stock_price, headers=headers, ticker=ticker)
    
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