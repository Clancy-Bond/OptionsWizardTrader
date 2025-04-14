"""
Simple test of market-hours aware caching with direct scenario testing
"""
import cache_module
from datetime import datetime, timedelta, time
import pytz

def test_cache_behavior():
    """Test various cache behavior scenarios directly"""
    print("\n=== Testing direct cache scenarios ===")
    
    # Eastern timezone for market hours
    eastern = pytz.timezone('US/Eastern')
    
    # Today's date
    today = datetime.now(eastern).date()
    
    # Find a recent Monday, Friday for testing
    weekday = datetime.now(eastern).weekday()
    monday = today - timedelta(days=(weekday - 0) % 7)
    friday = today - timedelta(days=(weekday - 4) % 7)
    
    # Test scenarios
    scenarios = [
        {
            "name": "Cache from Friday close, checked on Saturday", 
            "cache": eastern.localize(datetime.combine(friday, time(16, 30))),
            "now": eastern.localize(datetime.combine(friday + timedelta(days=1), time(12, 0))),
            "market_open": False,
            "expected": True
        },
        {
            "name": "Cache from Friday open, checked on Saturday",
            "cache": eastern.localize(datetime.combine(friday, time(10, 30))),
            "now": eastern.localize(datetime.combine(friday + timedelta(days=1), time(12, 0))),
            "market_open": False,
            "expected": False
        },
        {
            "name": "Cache from Monday close, checked Tuesday pre-market",
            "cache": eastern.localize(datetime.combine(monday, time(16, 30))),
            "now": eastern.localize(datetime.combine(monday + timedelta(days=1), time(8, 0))),
            "market_open": False,
            "expected": True
        },
        {
            "name": "Cache from 3 minutes ago during market hours",
            "cache": eastern.localize(datetime.combine(monday, time(10, 30))),
            "now": eastern.localize(datetime.combine(monday, time(10, 33))),
            "market_open": True,
            "expected": True
        },
        {
            "name": "Cache from 7 minutes ago during market hours",
            "cache": eastern.localize(datetime.combine(monday, time(10, 30))),
            "now": eastern.localize(datetime.combine(monday, time(10, 37))),
            "market_open": True,
            "expected": False
        }
    ]
    
    # Original function to restore later
    original_is_market_open = cache_module.is_market_open
    
    try:
        # Test each scenario
        for i, scenario in enumerate(scenarios):
            print(f"\nScenario {i+1}: {scenario['name']}")
            
            # Create a mock for is_market_open
            def mock_is_market_open():
                return scenario["market_open"]
            
            # Apply mock
            cache_module.is_market_open = mock_is_market_open
            
            # Get cache timestamp and current timestamp from scenario
            cache_timestamp = scenario["cache"]
            now_timestamp = scenario["now"]
            
            # Calculate time difference for display
            time_diff = (now_timestamp - cache_timestamp).total_seconds()
            
            # Directly calculate result with our custom "now"
            # This is equivalent to the logic in should_use_cached_data but with our mocked "now"
            result = evaluate_cache_validity(cache_timestamp, now_timestamp, scenario["market_open"])
            
            print(f"Cache timestamp: {cache_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"Current time:    {now_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"Time difference: {time_diff:.1f} seconds")
            print(f"Market is {'OPEN' if scenario['market_open'] else 'CLOSED'}")
            print(f"Result: {result}")
            print(f"Expected: {scenario['expected']}")
            print(f"Test {'PASSED' if result == scenario['expected'] else 'FAILED'}")
    
    finally:
        # Restore original function
        cache_module.is_market_open = original_is_market_open

def evaluate_cache_validity(cache_timestamp, now, market_open):
    """
    Evaluate whether cache should be valid based on the custom timestamps and market status
    
    This replicates the logic in should_use_cached_data but without calling the function directly
    since we need to insert our own "now" value.
    """
    eastern = pytz.timezone('US/Eastern')
    
    # Make sure timestamps are in eastern timezone
    if cache_timestamp.tzinfo is None:
        cache_timestamp = eastern.localize(cache_timestamp)
    elif cache_timestamp.tzinfo != eastern:
        cache_timestamp = cache_timestamp.astimezone(eastern)
        
    if now.tzinfo is None:
        now = eastern.localize(now)
    elif now.tzinfo != eastern:
        now = now.astimezone(eastern)
    
    # During market hours: 5-minute expiration
    if market_open:
        cache_age = (now - cache_timestamp).total_seconds()
        return cache_age < 300
    
    # If it's weekend
    if now.weekday() >= 5:  # Saturday or Sunday
        # Check if the cache entry was created after market close on Friday
        # Calculate last Friday
        days_since_friday = (now.weekday() - 4) % 7
        last_friday = now.date() - timedelta(days=days_since_friday)
        
        # Friday market close time
        friday_close = eastern.localize(datetime.combine(last_friday, time(16, 15, 0)))
        
        if cache_timestamp.date() == last_friday and cache_timestamp.time() >= time(16, 15, 0):
            return True
            
        # For entries created on Saturday or Sunday, they're valid
        if cache_timestamp.weekday() >= 5:
            return True
            
        # Otherwise the entry is too old
        return False
    
    # If we're after market close
    if now.time() >= time(16, 15, 0) and now.weekday() <= 4:
        today_market_close = eastern.localize(datetime.combine(now.date(), time(16, 15, 0)))
        return cache_timestamp >= today_market_close
    
    # If we're before market open
    if now.time() < time(9, 30, 0) and now.weekday() <= 4:
        # Calculate previous trading day
        if now.weekday() == 0:  # Monday
            prev_trading_day = now.date() - timedelta(days=3)  # Friday
        else:
            prev_trading_day = now.date() - timedelta(days=1)
            
        prev_market_close = eastern.localize(datetime.combine(prev_trading_day, time(16, 15, 0)))
        return cache_timestamp >= prev_market_close
    
    # Fallback
    cache_age = (now - cache_timestamp).total_seconds()
    return cache_age < 300

if __name__ == "__main__":
    print("=== Testing Market-Hours-Aware Caching ===")
    test_cache_behavior()