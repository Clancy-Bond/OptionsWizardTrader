# Quick test for institutional sentiment analysis
import polygon_integration as polygon
from unusual_activity import run_unusual_activity_test
import institutional_sentiment
import os
import json
import time

def test_with_cached_data(ticker):
    """Test with pre-loaded data to avoid API timeouts"""
    print(f"===== Testing Institutional Sentiment Analysis for {ticker} =====")
    
    # First try to load cached data if it exists
    cached_data = None
    try:
        if os.path.exists(f"{ticker}_cache.json"):
            with open(f"{ticker}_cache.json", "r") as f:
                cached_data = json.load(f)
                print(f"Loaded cached data for {ticker}")
    except Exception as e:
        print(f"Error loading cached data: {str(e)}")
    
    # If no cached data, make a fresh API call but limit the option count
    if not cached_data:
        print(f"No cached data found, fetching limited data for {ticker}")
        # Get a raw data sample with a small number of options
        raw_data = polygon.get_unusual_options_activity(ticker)
        
        # Save the data for future use
        try:
            with open(f"{ticker}_cache.json", "w") as f:
                json.dump(raw_data, f)
                print(f"Saved data to {ticker}_cache.json for future use")
        except Exception as e:
            print(f"Error saving data: {str(e)}")
    else:
        raw_data = cached_data
    
    # Analyze institutional sentiment
    if isinstance(raw_data, dict) and 'all_options_analyzed' in raw_data:
        print(f"Analyzing {raw_data.get('all_options_analyzed', 0)} options")
        
        # Check if institutional analysis was already performed
        if 'institutional_analysis' in raw_data:
            inst_analysis = raw_data.get('institutional_analysis', {})
            print("\n===== Institutional Sentiment Analysis =====")
            
            if inst_analysis.get('status') == 'success':
                sentiment = inst_analysis.get('sentiment', {})
                hedging_pct = inst_analysis.get('hedging_pct', 0)
                
                print(f"Hedging detected: {inst_analysis.get('hedging_detected', False)}")
                print(f"Hedging percentage: {hedging_pct:.1f}%")
                print(f"Hedging pairs: {inst_analysis.get('hedging_pairs', 0)}")
                
                # Print delta-weighted sentiment
                if 'bullish_delta_pct' in sentiment:
                    bull_pct = sentiment.get('bullish_delta_pct', 0)
                    bear_pct = sentiment.get('bearish_delta_pct', 0)
                    print(f"Bullish delta %: {bull_pct:.1f}%")
                    print(f"Bearish delta %: {bear_pct:.1f}%")
                    
                    # Determine overall sentiment
                    sentiment_desc = "neutral"
                    if bull_pct > 65:
                        sentiment_desc = "strongly bullish"
                    elif bull_pct > 55:
                        sentiment_desc = "moderately bullish"
                    elif bear_pct > 65:
                        sentiment_desc = "strongly bearish"
                    elif bear_pct > 55:
                        sentiment_desc = "moderately bearish"
                        
                    print(f"Overall institutional sentiment: {sentiment_desc}")
                
                # Print total trades analyzed
                if 'total_trades' in sentiment:
                    total_trades = sentiment.get('total_trades', 0)
                    directional = sentiment.get('directional_trades', 0)
                    print(f"Total trades analyzed: {total_trades}")
                    print(f"Directional trades: {directional}")
                    if total_trades > 0:
                        print(f"Non-directional ratio: {((total_trades - directional) / total_trades * 100):.1f}%")
                
                # Print strategy counts
                strategy_counts = inst_analysis.get('strategy_counts', {})
                if strategy_counts:
                    print("\nDetected strategies:")
                    for strategy, count in strategy_counts.items():
                        if count > 0:
                            print(f"  - {strategy}: {count}")
                
                # Print clustering info if available
                if 'clustering' in inst_analysis:
                    clustering = inst_analysis.get('clustering', {})
                    cluster_pct = clustering.get('cluster_pct', 0)
                    if cluster_pct > 25:  # Only show if significant clustering
                        print(f"\nTrade clustering detected: {cluster_pct:.1f}% of trades in largest cluster")
                        print(f"Largest cluster size: {clustering.get('largest_cluster', 0)} trades")
        else:
            # No institutional analysis yet, perform it now
            print("No institutional analysis in data, performing analysis now...")
            
            # Get the current stock price
            stock_price = polygon.get_current_price(ticker)
            
            # Convert unusual options activity to the format expected by institutional sentiment
            option_trades = []
            for opt in raw_data.get('unusual_options', []):
                # Create a simplified trade object for analysis
                trade = {
                    'symbol': opt.get('contract', ''),
                    'contract_type': 'call' if opt.get('sentiment') == 'bullish' else 'put',
                    'size': opt.get('contract_volume', 1),
                    'price': opt.get('avg_price', 0),
                    'premium': opt.get('premium', 0) / 100,  # Convert to per-contract premium
                    'sentiment': opt.get('sentiment', ''),
                    'timestamp': int(time.time())
                }
                option_trades.append(trade)
            
            # Analyze sentiment
            analysis = institutional_sentiment.analyze_institutional_sentiment(option_trades, stock_price)
            
            # Get human-readable summary
            summary = institutional_sentiment.get_human_readable_summary(analysis, ticker)
            
            print("\n" + summary)
    else:
        print("No valid option data available for analysis")

if __name__ == "__main__":
    # Test with a ticker symbol
    test_with_cached_data("SPY")