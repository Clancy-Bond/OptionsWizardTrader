"""
Enhanced institutional sentiment analysis module for OptionsWizard

This module provides advanced analysis of options trades to better identify
true institutional sentiment while filtering out hedging activities.

Key features:
1. Hedge detection using time correlation and position analysis
2. Options strategy detection (spreads, volatility strategies)
3. Enhanced sentiment scoring using delta weighting and premium analysis
"""

import time
import random
from datetime import datetime, timedelta
import numpy as np
from math import log, sqrt, exp
from scipy.stats import norm
import pandas as pd

# Constants for analysis
MAX_HEDGE_TIME_WINDOW = 3600  # 1 hour in seconds (increased from 10 minutes for Polygon API data)
TYPICAL_HEDGE_RATIO = 0.5  # Typical size ratio for hedging trades (50% match - relaxed from 80%)
DEEP_OTM_THRESHOLD = 0.2  # 20% OTM is considered "deep"
MIN_HEDGE_SIZE = 3  # Minimum contract size to consider for hedge detection (reduced from 5)
CLUSTER_WINDOW = 7200  # 2 hours in seconds for clustering trades

def calculate_option_delta(option_data, stock_price=None):
    """
    Calculate the delta of an option using the Black-Scholes model

    Args:
        option_data: Dictionary containing option information
        stock_price: Current stock price (if not provided, uses strike * 0.98 for puts, strike * 1.02 for calls)

    Returns:
        Delta value between 0-1 (absolute value)
    """
    # Extract option parameters
    strike = option_data.get('strike_price', 0)
    days_to_expiration = option_data.get('days_to_expiration', 30)
    option_type = option_data.get('contract_type', '').lower()
    
    # If no stock price provided, estimate based on option type
    if not stock_price:
        stock_price = strike * 1.02 if option_type == 'call' else strike * 0.98
    
    # Use reasonable defaults for volatility and interest rate if not available
    volatility = option_data.get('implied_volatility', 0.3)
    risk_free_rate = 0.05
    
    # Convert days to years
    time_to_expiration = days_to_expiration / 365.0
    
    # Avoid division by zero or negative time
    if time_to_expiration <= 0:
        return 1.0 if option_type == 'call' and stock_price > strike else 0.0
    
    # Calculate d1 from Black-Scholes
    try:
        d1 = (log(stock_price / strike) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiration) / (volatility * sqrt(time_to_expiration))
        
        # Calculate delta
        if option_type == 'call':
            delta = norm.cdf(d1)
        else:  # put
            delta = -norm.cdf(-d1)
    except (ValueError, ZeroDivisionError):
        # Fallback for calculation errors
        if option_type == 'call':
            delta = 1.0 if stock_price > strike else 0.0
        else:
            delta = -1.0 if stock_price < strike else 0.0
    
    return abs(delta)  # Return absolute value for consistent comparison

def detect_hedging_pairs(options_trades):
    """
    Detect potential hedging pairs in a list of options trades
    
    Args:
        options_trades: List of option trade dictionaries
        
    Returns:
        List of trade pairs that are likely hedging activities
    """
    # Sort trades by timestamp
    sorted_trades = sorted(options_trades, key=lambda x: x.get('timestamp', 0))
    
    # Initialize results
    hedging_pairs = []
    
    # Compare each trade with subsequent trades within time window
    for i, trade in enumerate(sorted_trades):
        trade_size = trade.get('size', 0)
        trade_sentiment = trade.get('sentiment')
        trade_time = trade.get('timestamp', 0)
        
        # Skip small trades
        if trade_size < MIN_HEDGE_SIZE:
            continue
        
        # Look for offsetting trades within time window
        for j in range(i+1, len(sorted_trades)):
            compare_trade = sorted_trades[j]
            compare_time = compare_trade.get('timestamp', 0)
            compare_size = compare_trade.get('size', 0)
            compare_sentiment = compare_trade.get('sentiment')
            
            # Skip small trades
            if compare_size < MIN_HEDGE_SIZE:
                continue
            
            # Check if within time window
            if compare_time - trade_time > MAX_HEDGE_TIME_WINDOW:
                break  # Exceeded time window, stop looking
            
            # Check for opposing sentiment
            if trade_sentiment != compare_sentiment and trade_sentiment is not None and compare_sentiment is not None:
                # Calculate size ratio (smaller/larger)
                size_ratio = min(trade_size, compare_size) / max(trade_size, compare_size)
                
                # If size is similar (within hedge ratio threshold), likely a hedge
                if size_ratio >= TYPICAL_HEDGE_RATIO:
                    hedging_pairs.append({
                        'trade1': trade,
                        'trade2': compare_trade,
                        'size_ratio': size_ratio,
                        'time_diff': compare_time - trade_time,
                        'hedge_probability': size_ratio * (1 - (compare_time - trade_time) / MAX_HEDGE_TIME_WINDOW)
                    })
    
    return hedging_pairs

def detect_option_strategies(options_trades):
    """
    Detect common options strategies in trade data
    
    Args:
        options_trades: List of option trade dictionaries
        
    Returns:
        Dictionary mapping strategy types to lists of trades
    """
    # Sort trades by timestamp
    sorted_trades = sorted(options_trades, key=lambda x: x.get('timestamp', 0))
    
    # Initialize results
    strategies = {
        'vertical_spreads': [],
        'calendar_spreads': [],
        'straddles': [],
        'strangles': [],
        'iron_condors': [],
        'scale_ins': []
    }
    
    # Group trades by option symbol base (ticker + expiration)
    ticker_exp_groups = {}
    for trade in sorted_trades:
        # Extract ticker and expiration from the option symbol
        symbol = trade.get('symbol', '')
        ticker = symbol.split('_')[0] if '_' in symbol else ''
        expiration = trade.get('expiration_date', '')
        
        # Skip if missing data
        if not ticker or not expiration:
            continue
        
        key = f"{ticker}_{expiration}"
        if key not in ticker_exp_groups:
            ticker_exp_groups[key] = []
        
        ticker_exp_groups[key].append(trade)
    
    # Detect vertical spreads (same expiration, different strikes, opposite directions)
    for key, trades in ticker_exp_groups.items():
        # Group trades by strike
        strike_groups = {}
        for trade in trades:
            strike = trade.get('strike_price', 0)
            if strike not in strike_groups:
                strike_groups[strike] = []
            strike_groups[strike].append(trade)
        
        # Look for trade pairs with different strikes
        strikes = sorted(strike_groups.keys())
        for i, strike1 in enumerate(strikes):
            for strike2 in strikes[i+1:]:
                # Analyze trade pairs across these two strikes
                for trade1 in strike_groups[strike1]:
                    for trade2 in strike_groups[strike2]:
                        # Check if time difference is small
                        time_diff = abs(trade1.get('timestamp', 0) - trade2.get('timestamp', 0))
                        if time_diff <= MAX_HEDGE_TIME_WINDOW:
                            # Check for vertical spread pattern
                            if (trade1.get('contract_type') == trade2.get('contract_type') and
                                trade1.get('size', 0) == trade2.get('size', 0)):
                                strategies['vertical_spreads'].append({
                                    'trade1': trade1,
                                    'trade2': trade2,
                                    'time_diff': time_diff,
                                    'strategy': 'Bull Spread' if trade1.get('contract_type').lower() == 'call' else 'Bear Spread'
                                })
    
    # Group trades by strike across different expirations for calendar spreads
    strike_groups = {}
    for trade in sorted_trades:
        strike = trade.get('strike_price', 0)
        if strike not in strike_groups:
            strike_groups[strike] = []
        strike_groups[strike].append(trade)
    
    # Detect calendar spreads (same strike, different expirations)
    for strike, trades in strike_groups.items():
        # Sort by expiration
        trades_by_exp = sorted(trades, key=lambda x: x.get('expiration_date', ''))
        
        # Compare trades with different expirations
        for i, trade1 in enumerate(trades_by_exp):
            for trade2 in trades_by_exp[i+1:]:
                # Check if same contract type and similar size
                if (trade1.get('contract_type') == trade2.get('contract_type') and
                    abs(trade1.get('size', 0) - trade2.get('size', 0)) <= 2):
                    # Check time difference
                    time_diff = abs(trade1.get('timestamp', 0) - trade2.get('timestamp', 0))
                    if time_diff <= MAX_HEDGE_TIME_WINDOW:
                        strategies['calendar_spreads'].append({
                            'trade1': trade1,
                            'trade2': trade2,
                            'time_diff': time_diff
                        })
    
    # Detect straddles/strangles (same expiration, similar strikes, different option types)
    for key, trades in ticker_exp_groups.items():
        call_trades = [t for t in trades if t.get('contract_type', '').lower() == 'call']
        put_trades = [t for t in trades if t.get('contract_type', '').lower() == 'put']
        
        # Compare each call with each put
        for call in call_trades:
            call_strike = call.get('strike_price', 0)
            for put in put_trades:
                put_strike = put.get('strike_price', 0)
                
                # Calculate strike difference as percentage
                avg_strike = (call_strike + put_strike) / 2
                strike_diff_pct = abs(call_strike - put_strike) / avg_strike if avg_strike > 0 else 1
                
                # Check time difference
                time_diff = abs(call.get('timestamp', 0) - put.get('timestamp', 0))
                
                # Straddle: same strike for call and put
                if strike_diff_pct < 0.01 and time_diff <= MAX_HEDGE_TIME_WINDOW:
                    strategies['straddles'].append({
                        'call': call,
                        'put': put,
                        'time_diff': time_diff
                    })
                # Strangle: different but close strikes
                elif strike_diff_pct < 0.05 and time_diff <= MAX_HEDGE_TIME_WINDOW:
                    strategies['strangles'].append({
                        'call': call,
                        'put': put,
                        'time_diff': time_diff,
                        'strike_diff_pct': strike_diff_pct
                    })
    
    # Detect scale-ins (same option, multiple trades over time)
    option_accumulation = {}
    for trade in sorted_trades:
        symbol = trade.get('symbol', '')
        if not symbol:
            continue
        
        if symbol not in option_accumulation:
            option_accumulation[symbol] = []
        
        option_accumulation[symbol].append(trade)
    
    # Find options with multiple trades over time
    for symbol, trades in option_accumulation.items():
        if len(trades) >= 3:  # At least 3 trades to consider a pattern
            # Sort by timestamp
            time_sorted = sorted(trades, key=lambda x: x.get('timestamp', 0))
            
            # Check if accumulating (increasing position)
            total_size = sum(t.get('size', 0) for t in time_sorted)
            time_span = time_sorted[-1].get('timestamp', 0) - time_sorted[0].get('timestamp', 0)
            
            # Consider it a scale-in if spread over at least 1 hour
            if time_span >= 3600 and total_size >= 20:
                strategies['scale_ins'].append({
                    'symbol': symbol,
                    'trades': time_sorted,
                    'total_size': total_size,
                    'time_span': time_span
                })
    
    return strategies

def calculate_enhanced_sentiment_score(option_trades, stock_price):
    """
    Calculate enhanced sentiment scores that account for delta, premium, and trade patterns
    
    Args:
        option_trades: List of option trade dictionaries
        stock_price: Current stock price
        
    Returns:
        Dictionary with detailed sentiment metrics
    """
    # Initialize counters
    total_bullish_delta = 0
    total_bearish_delta = 0
    total_bullish_premium = 0
    total_bearish_premium = 0
    total_bullish_contracts = 0
    total_bearish_contracts = 0
    
    # Detect hedging pairs and strategies
    hedging_pairs = detect_hedging_pairs(option_trades)
    strategies = detect_option_strategies(option_trades)
    
    # Create a set of trades to exclude (part of hedging or spreads)
    excluded_trades = set()
    
    # Exclude hedging pairs from directional sentiment
    for pair in hedging_pairs:
        # Mark trades as part of hedge
        if 'trade1' in pair and isinstance(pair['trade1'], dict) and 'id' in pair['trade1']:
            excluded_trades.add(pair['trade1']['id'])
        if 'trade2' in pair and isinstance(pair['trade2'], dict) and 'id' in pair['trade2']:
            excluded_trades.add(pair['trade2']['id'])
    
    # Exclude spreads and other strategies
    for strategy_type, strategy_list in strategies.items():
        for strategy in strategy_list:
            # Different strategies have different structure, handle each case
            if strategy_type in ['vertical_spreads', 'calendar_spreads']:
                if 'trade1' in strategy and isinstance(strategy['trade1'], dict) and 'id' in strategy['trade1']:
                    excluded_trades.add(strategy['trade1']['id'])
                if 'trade2' in strategy and isinstance(strategy['trade2'], dict) and 'id' in strategy['trade2']:
                    excluded_trades.add(strategy['trade2']['id'])
            elif strategy_type in ['straddles', 'strangles']:
                if 'call' in strategy and isinstance(strategy['call'], dict) and 'id' in strategy['call']:
                    excluded_trades.add(strategy['call']['id'])
                if 'put' in strategy and isinstance(strategy['put'], dict) and 'id' in strategy['put']:
                    excluded_trades.add(strategy['put']['id'])
    
    # Process each trade that isn't part of a hedge or spread
    directional_trades = []
    for trade in option_trades:
        # Skip trades that are part of hedging or strategies
        trade_id = trade.get('id', '')
        if trade_id in excluded_trades:
            continue
        
        # Add to directional trades for analysis
        directional_trades.append(trade)
        
        # Get basic trade information
        contract_type = trade.get('contract_type', '').lower()
        sentiment = 'bullish' if contract_type == 'call' else 'bearish'
        contracts = trade.get('size', 0)
        premium = trade.get('price', 0) * contracts * 100  # Convert to total premium
        
        # Calculate delta for this option
        delta = calculate_option_delta(trade, stock_price)
        
        # Weight by delta (directional exposure)
        delta_weighted_contracts = contracts * delta
        
        # Add to totals
        if sentiment == 'bullish':
            total_bullish_delta += delta_weighted_contracts
            total_bullish_premium += premium
            total_bullish_contracts += contracts
        else:
            total_bearish_delta += delta_weighted_contracts
            total_bearish_premium += premium
            total_bearish_contracts += contracts
    
    # Calculate new sentiment metrics
    total_delta = total_bullish_delta + total_bearish_delta
    total_premium = total_bullish_premium + total_bearish_premium
    total_contracts = total_bullish_contracts + total_bearish_contracts
    
    # Calculate percentages
    if total_delta > 0:
        bullish_delta_pct = (total_bullish_delta / total_delta) * 100
        bearish_delta_pct = (total_bearish_delta / total_delta) * 100
    else:
        bullish_delta_pct = 50
        bearish_delta_pct = 50
    
    if total_premium > 0:
        bullish_premium_pct = (total_bullish_premium / total_premium) * 100
        bearish_premium_pct = (total_bearish_premium / total_premium) * 100
    else:
        bullish_premium_pct = 50
        bearish_premium_pct = 50
    
    if total_contracts > 0:
        bullish_contract_pct = (total_bullish_contracts / total_contracts) * 100
        bearish_contract_pct = (total_bearish_contracts / total_contracts) * 100
    else:
        bullish_contract_pct = 50
        bearish_contract_pct = 50
    
    # Create summary
    sentiment_summary = {
        # Delta-weighted metrics (primary)
        'bullish_delta': total_bullish_delta,
        'bearish_delta': total_bearish_delta,
        'bullish_delta_pct': bullish_delta_pct,
        'bearish_delta_pct': bearish_delta_pct,
        
        # Premium metrics
        'bullish_premium': total_bullish_premium,
        'bearish_premium': total_bearish_premium,
        'bullish_premium_pct': bullish_premium_pct,
        'bearish_premium_pct': bearish_premium_pct,
        
        # Contract metrics (traditional)
        'bullish_contracts': total_bullish_contracts,
        'bearish_contracts': total_bearish_contracts,
        'bullish_contract_pct': bullish_contract_pct,
        'bearish_contract_pct': bearish_contract_pct,
        
        # Strategy information
        'hedging_pairs_count': len(hedging_pairs),
        'vertical_spreads_count': len(strategies['vertical_spreads']),
        'calendar_spreads_count': len(strategies['calendar_spreads']),
        'straddles_count': len(strategies['straddles']),
        'strangles_count': len(strategies['strangles']),
        'scale_ins_count': len(strategies['scale_ins']),
        
        # Overall counts
        'total_trades': len(option_trades),
        'directional_trades': len(directional_trades),
        'hedging_trades': len(excluded_trades)
    }
    
    # Add a single sentiment indicator (normalized weighted average of delta and premium)
    # Higher values indicate more bullish sentiment (0-100)
    weighted_sentiment = (bullish_delta_pct * 0.6) + (bullish_premium_pct * 0.4)
    sentiment_summary['weighted_sentiment'] = weighted_sentiment
    
    # Determine overall sentiment category
    if weighted_sentiment >= 65:
        sentiment_summary['overall_sentiment'] = 'strongly_bullish'
    elif weighted_sentiment >= 55:
        sentiment_summary['overall_sentiment'] = 'moderately_bullish'
    elif weighted_sentiment >= 45:
        sentiment_summary['overall_sentiment'] = 'neutral'
    elif weighted_sentiment >= 35:
        sentiment_summary['overall_sentiment'] = 'moderately_bearish'
    else:
        sentiment_summary['overall_sentiment'] = 'strongly_bearish'
    
    return sentiment_summary

def analyze_institutional_sentiment(option_trades, stock_price):
    """
    Main entry point for institutional sentiment analysis
    
    Args:
        option_trades: List of option trade dictionaries
        stock_price: Current stock price
        
    Returns:
        Dictionary with sentiment analysis results
    """
    try:
        # Force numeric timestamps for analysis
        for trade in option_trades:
            if 'timestamp' not in trade or not isinstance(trade.get('timestamp'), (int, float)):
                # Generate a synthetic timestamp if missing
                trade['timestamp'] = int(time.time() - (3600 * random.randint(0, 24)))
        
        # Skip analysis if insufficient data
        if not option_trades or len(option_trades) < 5:
            return {
                'status': 'insufficient_data',
                'message': f'Insufficient data for institutional analysis ({len(option_trades)} trades)'
            }
        
        # Ensure trades have IDs for tracking
        for i, trade in enumerate(option_trades):
            if 'id' not in trade or not trade['id']:
                trade['id'] = f"trade_{i}_{trade.get('contract_type', '')}_{trade.get('strike_price', 0)}"
        
        print(f"Analyzing {len(option_trades)} trades for institutional sentiment")
        
        # Calculate enhanced sentiment metrics
        sentiment = calculate_enhanced_sentiment_score(option_trades, stock_price)
        
        # Get details on hedging and strategies
        hedging_pairs = detect_hedging_pairs(option_trades)
        strategies = detect_option_strategies(option_trades)
        
        # Calculate hedging percentage - more safely with error handling
        total_trades = len(option_trades)
        hedged_trade_ids = set()
        
        for pair in hedging_pairs:
            if 'trade1' in pair and isinstance(pair['trade1'], dict) and 'id' in pair['trade1']:
                hedged_trade_ids.add(pair['trade1']['id'])
            if 'trade2' in pair and isinstance(pair['trade2'], dict) and 'id' in pair['trade2']:
                hedged_trade_ids.add(pair['trade2']['id'])
        
        hedged_trades = len(hedged_trade_ids)
        hedging_pct = (hedged_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Generate histogram of trade timestamps to detect trade clustering
        timestamps = [trade.get('timestamp', 0) for trade in option_trades]
        timestamp_clusters = {}
        
        # Cluster timestamps into N-minute windows
        window_size = 900  # 15 minute windows
        for ts in timestamps:
            window = ts - (ts % window_size)
            if window not in timestamp_clusters:
                timestamp_clusters[window] = 0
            timestamp_clusters[window] += 1
        
        # Find the largest cluster
        largest_cluster = max(timestamp_clusters.values()) if timestamp_clusters else 0
        cluster_pct = (largest_cluster / total_trades) * 100 if total_trades > 0 else 0
        
        # Determine overall sentiment based on delta percentages
        bullish_delta_pct = sentiment.get('bullish_delta_pct', 50)
        bearish_delta_pct = sentiment.get('bearish_delta_pct', 50)
        
        if bullish_delta_pct > 65:
            overall_sentiment = "strongly_bullish"
        elif bullish_delta_pct > 55:
            overall_sentiment = "moderately_bullish"
        elif bearish_delta_pct > 65:
            overall_sentiment = "strongly_bearish"
        elif bearish_delta_pct > 55:
            overall_sentiment = "moderately_bearish"
        else:
            overall_sentiment = "neutral"
            
        # Add overall sentiment to the results
        sentiment['overall_sentiment'] = overall_sentiment
        sentiment['total_trades'] = total_trades
        sentiment['directional_trades'] = total_trades - hedged_trades
        
        # Reformat results for cleaner output
        results = {
            'status': 'success',
            'sentiment': sentiment,
            'hedging_detected': hedged_trades > 5,  # Require at least 5 hedged trades to consider it significant
            'hedging_pairs': len(hedging_pairs),
            'hedging_pct': hedging_pct,
            'strategy_counts': {
                'vertical_spreads': len(strategies['vertical_spreads']),
                'calendar_spreads': len(strategies['calendar_spreads']),
                'straddles': len(strategies['straddles']),
                'strangles': len(strategies['strangles']),
                'scale_ins': len(strategies['scale_ins'])
            },
            'clustering': {
                'largest_cluster': largest_cluster,
                'cluster_pct': cluster_pct
            }
        }
        
        # Log analysis results
        print(f"Institutional sentiment analysis: {overall_sentiment} with {hedging_pct:.1f}% hedging detected")
        print(f"Bullish: {bullish_delta_pct:.1f}%, Bearish: {bearish_delta_pct:.1f}%, Total trades: {total_trades}")
        
    except Exception as e:
        print(f"Error in institutional sentiment analysis: {str(e)}")
        results = {
            'status': 'error',
            'message': str(e)
        }
    
    return results

def get_human_readable_summary(analysis_results, ticker):
    """
    Create a human-readable summary of the institutional sentiment analysis
    
    Args:
        analysis_results: Results from analyze_institutional_sentiment()
        ticker: The ticker symbol
        
    Returns:
        String with human-readable summary
    """
    if analysis_results.get('status') != 'success':
        return f"Insufficient data for institutional analysis of {ticker}"
    
    sentiment = analysis_results.get('sentiment', {})
    
    # Get the main sentiment metrics
    bullish_delta_pct = sentiment.get('bullish_delta_pct', 50)
    bearish_delta_pct = sentiment.get('bearish_delta_pct', 50)
    
    bullish_premium = sentiment.get('bullish_premium', 0) / 1000000  # Convert to millions
    bearish_premium = sentiment.get('bearish_premium', 0) / 1000000  # Convert to millions
    
    # Get strategy information
    hedging_pct = analysis_results.get('hedging_pct', 0)
    strategy_counts = analysis_results.get('strategy_counts', {})
    
    # Determine sentiment description
    overall_sentiment = sentiment.get('overall_sentiment', 'neutral')
    
    if overall_sentiment == 'strongly_bullish':
        sentiment_desc = "strongly bullish"
    elif overall_sentiment == 'moderately_bullish':
        sentiment_desc = "moderately bullish"
    elif overall_sentiment == 'neutral':
        sentiment_desc = "neutral"
    elif overall_sentiment == 'moderately_bearish':
        sentiment_desc = "moderately bearish"
    else:
        sentiment_desc = "strongly bearish"
    
    # Create detailed summary string
    summary = f"🏦 Institutional Sentiment Analysis for {ticker} 🏦\n\n"
    
    # Overall sentiment
    summary += f"• True institutional sentiment is {sentiment_desc} after filtering out detected hedging activities.\n"
    
    # Key metrics
    summary += f"• Delta-weighted flow: {bullish_delta_pct:.1f}% bullish / {bearish_delta_pct:.1f}% bearish\n"
    summary += f"• Capital deployment: ${bullish_premium:.2f}M bullish / ${bearish_premium:.2f}M bearish\n"
    
    # Hedging
    if hedging_pct > 5:
        summary += f"• Detected significant hedging activity ({hedging_pct:.1f}% of trades), which has been filtered out\n"
    
    # Strategy insights
    strategies_detected = []
    if strategy_counts.get('vertical_spreads', 0) > 2:
        strategies_detected.append(f"{strategy_counts['vertical_spreads']} vertical spreads")
    if strategy_counts.get('calendar_spreads', 0) > 2:
        strategies_detected.append(f"{strategy_counts['calendar_spreads']} calendar spreads")
    if strategy_counts.get('straddles', 0) + strategy_counts.get('strangles', 0) > 2:
        strat_count = strategy_counts.get('straddles', 0) + strategy_counts.get('strangles', 0)
        strategies_detected.append(f"{strat_count} volatility strategies")
    if strategy_counts.get('scale_ins', 0) > 2:
        strategies_detected.append(f"{strategy_counts['scale_ins']} accumulation patterns")
    
    if strategies_detected:
        summary += "• Detected sophisticated strategies: " + ", ".join(strategies_detected) + "\n"
    
    # Total trades analyzed
    total_trades = sentiment.get('total_trades', 0)
    directional_trades = sentiment.get('directional_trades', 0)
    summary += f"\nAnalysis based on {total_trades} trades, with {directional_trades} directional trades and {total_trades - directional_trades} hedging/strategy trades."
    
    return summary