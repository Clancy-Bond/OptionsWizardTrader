"""
Test script to verify that "Overall flow" percentages are calculated from all unusual options
and not just the top 5.
"""
import polygon_integration
import cache_module
import re

def test_unusual_options_flow(ticker):
    """Test unusual options flow calculation for a given ticker"""
    print(f"\n=== Testing unusual options flow for {ticker} ===")
    
    # Use cache if available to avoid API calls
    if cache_module.cache_contains(ticker):
        print(f"Found {ticker} in cache, using cached data")
    else:
        print(f"No cache entry for {ticker}, will fetch fresh data")
    
    # Get the simplified summary (which uses the overall sentiment)
    print(f"Getting simplified summary for {ticker}...")
    summary = polygon_integration.get_simplified_unusual_activity_summary(ticker)
    
    # Extract the overall flow percentages from the summary
    flow_pattern = r"Overall flow: (\d+)% bullish / (\d+)% bearish"
    flow_match = re.search(flow_pattern, summary)
    
    if flow_match:
        bullish_pct = int(flow_match.group(1))
        bearish_pct = int(flow_match.group(2))
        print(f"\nFound flow percentages in summary: {bullish_pct}% bullish / {bearish_pct}% bearish")
        
        # Verify that bullish_pct + bearish_pct = 100%
        if bullish_pct + bearish_pct != 100:
            print(f"ERROR: Percentages don't add up to 100%! ({bullish_pct}% + {bearish_pct}% = {bullish_pct + bearish_pct}%)")
        else:
            print("Percentages correctly add up to 100%")
            
        # For cached data, check if the percentages are calculated from all unusual options
        cached_data = cache_module.get_from_cache(ticker)[0]
        if cached_data and isinstance(cached_data, dict):
            total_bullish = cached_data.get('total_bullish_count', 0)
            total_bearish = cached_data.get('total_bearish_count', 0)
            total_options = total_bullish + total_bearish
            
            if total_options > 0:
                expected_bullish_pct = round((total_bullish / total_options) * 100)
                expected_bearish_pct = round((total_bearish / total_options) * 100)
                
                print(f"\nExpected percentages based on ALL unusual options: {expected_bullish_pct}% bullish / {expected_bearish_pct}% bearish")
                print(f"Actual percentages in summary: {bullish_pct}% bullish / {bearish_pct}% bearish")
                
                if expected_bullish_pct == bullish_pct and expected_bearish_pct == bearish_pct:
                    print("SUCCESS: Flow percentages are calculated from ALL unusual options!")
                else:
                    print("ERROR: Flow percentages don't match expected values from all unusual options!")
    else:
        print("Could not find flow percentages in summary")
        print(f"Summary: {summary}")

if __name__ == "__main__":
    # Test with a single ticker first
    test_unusual_options_flow("TSLA")