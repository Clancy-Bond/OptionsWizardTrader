"""
Test the market-hours-aware caching functionality
"""
import cache_module
from datetime import datetime, timedelta
import pytz

def print_market_status():
    """Print current market status based on time"""
    is_open = cache_module.is_market_open()
    print(f"Market is currently {'OPEN' if is_open else 'CLOSED'}")
    
    # Get current time in ET
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    print(f"Current time (ET): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Day of week: {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][now.weekday()]}")

def test_with_simulated_timestamps():
    """Test cache behavior with simulated timestamps"""
    print("\n=== Testing with simulated timestamps ===")
    eastern = pytz.timezone('US/Eastern')
    
    # Test scenarios
    scenarios = [
        # Weekend scenarios
        {
            "name": "Cache from Friday close, checked on Saturday",
            "cache_time": "Friday 16:30",
            "check_time": "Saturday 12:00", 
            "expected": True
        },
        {
            "name": "Cache from Friday open, checked on Saturday",
            "cache_time": "Friday 10:30",
            "check_time": "Saturday 12:00",
            "expected": False
        },
        {
            "name": "Cache from Friday close, checked on Sunday",
            "cache_time": "Friday 16:30",
            "check_time": "Sunday 12:00",
            "expected": True
        },
        
        # Weekday after-hours scenarios
        {
            "name": "Cache from Monday close, checked Tuesday pre-market",
            "cache_time": "Monday 16:30",
            "check_time": "Tuesday 8:00",
            "expected": True
        },
        {
            "name": "Cache from Monday open, checked Monday after-hours",
            "cache_time": "Monday 10:30",
            "check_time": "Monday 17:00",
            "expected": False
        },
        {
            "name": "Cache from Monday after-hours, checked Tuesday pre-market",
            "cache_time": "Monday 17:30",
            "check_time": "Tuesday 8:00",
            "expected": True
        },
        
        # Market hours scenarios
        {
            "name": "Cache from 3 minutes ago during market hours",
            "cache_time": "Monday 10:30",
            "check_time": "Monday 10:33",
            "expected": True
        },
        {
            "name": "Cache from 7 minutes ago during market hours",
            "cache_time": "Monday 10:30",
            "check_time": "Monday 10:37",
            "expected": False
        }
    ]
    
    # Get current time as reference
    now = datetime.now(eastern)
    current_weekday = now.weekday()
    
    # Find the last Friday if today is not Friday
    days_to_friday = (current_weekday - 4) % 7
    last_friday = now.date() - timedelta(days=days_to_friday)
    
    # Find the last Monday if today is not Monday
    days_to_monday = (current_weekday - 0) % 7
    last_monday = now.date() - timedelta(days=days_to_monday)
    
    # Test each scenario
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        
        # Parse the day and time
        cache_day, cache_time = scenario['cache_time'].split()
        check_day, check_time = scenario['check_time'].split()
        
        # Set the appropriate date based on day name
        if cache_day == "Friday":
            cache_date = last_friday
        elif cache_day == "Saturday":
            cache_date = last_friday + timedelta(days=1)
        elif cache_day == "Sunday": 
            cache_date = last_friday + timedelta(days=2)
        elif cache_day == "Monday":
            cache_date = last_monday
        elif cache_day == "Tuesday":
            cache_date = last_monday + timedelta(days=1)
            
        if check_day == "Friday":
            check_date = last_friday
        elif check_day == "Saturday":
            check_date = last_friday + timedelta(days=1)
        elif check_day == "Sunday":
            check_date = last_friday + timedelta(days=2)
        elif check_day == "Monday":
            check_date = last_monday
        elif check_day == "Tuesday":
            check_date = last_monday + timedelta(days=1)
            
        # Create datetime objects with the specified times
        cache_hour, cache_minute = map(int, cache_time.split(':'))
        check_hour, check_minute = map(int, check_time.split(':'))
        
        cache_datetime = eastern.localize(datetime.combine(cache_date, datetime.min.time().replace(hour=cache_hour, minute=cache_minute)))
        check_datetime = eastern.localize(datetime.combine(check_date, datetime.min.time().replace(hour=check_hour, minute=check_minute)))
        
        # Now check if it would be valid
        result = cache_module.should_use_cached_data(cache_datetime)
        print(f"Cache timestamp: {cache_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Check timestamp: {check_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Simulated result: {result}")
        print(f"Expected result: {scenario['expected']}")
        print(f"Test {'PASSED' if result == scenario['expected'] else 'FAILED'}")

def test_live_caching():
    """Test caching with actual timestamps"""
    print("\n=== Testing with live timestamps ===")
    
    # Add test data to cache
    cache_module.add_to_cache("TEST_TICKER", ["Test data"])
    
    # Print cache contents
    cache_module.print_cache_contents()
    
    # Try retrieving from cache
    data, found = cache_module.get_from_cache("TEST_TICKER")
    print(f"Retrieved data successfully: {found}")
    
    # Clear test data
    if "TEST_TICKER" in cache_module.unusual_activity_cache:
        del cache_module.unusual_activity_cache["TEST_TICKER"]

if __name__ == "__main__":
    print("=== Testing Market-Hours-Aware Caching ===")
    print_market_status()
    test_with_simulated_timestamps()
    test_live_caching()