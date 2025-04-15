"""
Test script to analyze SPY options with no limit
"""
import sys
from polygon_integration import get_unusual_options_activity

ticker = "SPY"
print(f"Analyzing all near-the-money options for {ticker}...")
result = get_unusual_options_activity(ticker)

# Print detailed results
if result:
    print(f"\nAnalysis complete.")
    print(f"Total options analyzed: {result.get('all_options_analyzed', 0)}")
    print(f"Bullish contracts: {result.get('total_bullish_count', 0)}")
    print(f"Bearish contracts: {result.get('total_bearish_count', 0)}")
    
    if result.get('total_bullish_count', 0) + result.get('total_bearish_count', 0) > 0:
        bullish_pct = result.get('total_bullish_count', 0) / (result.get('total_bullish_count', 0) + result.get('total_bearish_count', 0)) * 100
        bearish_pct = result.get('total_bearish_count', 0) / (result.get('total_bullish_count', 0) + result.get('total_bearish_count', 0)) * 100
        print(f"Sentiment breakdown: {bullish_pct:.1f}% bullish / {bearish_pct:.1f}% bearish")
    
    # Print the top 5 unusual options
    unusual_options = result.get('unusual_options', [])
    print(f"\nNumber of unusual options detected: {len(unusual_options)}")
    
    print("\nTop 5 most unusual options:")
    for idx, option in enumerate(unusual_options[:5]):
        print(f"  {idx+1}. {option.get('contract', 'Unknown')} - Score: {option.get('unusualness_score', 0)}")
        print(f"     Premium: ${option.get('premium', 0)/1000000:.2f}M - Sentiment: {option.get('sentiment', 'Unknown')}")
else:
    print("No results returned from analysis.")