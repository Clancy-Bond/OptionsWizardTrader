"""
Test the market-hours-aware caching functionality
"""
import cache_module
from datetime import datetime, timedelta, time
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

def test_with_mocked_market_conditions():
    """
    Test cache behavior with mocked market conditions
    
    This function temporarily patches the is_market_open and datetime.now functions
    to simulate different market conditions for each test scenario
    """
    print("\n=== Testing with mocked market conditions ===")
    
    # Original functions to restore later
    original_is_market_open = cache_module.is_market_open
    original_datetime_now = datetime.now
    
    try:
        # Test scenarios
        scenarios = [
            # Weekend scenarios
            {
                "name": "Cache from Friday close, checked on Saturday",
                "cache_day": 4,  # Friday
                "cache_hour": 16,
                "cache_minute": 30,
                "check_day": 5,  # Saturday
                "check_hour": 12,
                "check_minute": 0,
                "expected": True
            },
            {
                "name": "Cache from Friday open, checked on Saturday",
                "cache_day": 4,  # Friday
                "cache_hour": 10,
                "cache_minute": 30,
                "check_day": 5,  # Saturday
                "check_hour": 12,
                "check_minute": 0,
                "expected": False
            },
            {
                "name": "Cache from Friday close, checked on Sunday",
                "cache_day": 4,  # Friday
                "cache_hour": 16,
                "cache_minute": 30,
                "check_day": 6,  # Sunday
                "check_hour": 12,
                "check_minute": 0,
                "expected": True
            },
            
            # Weekday after-hours scenarios
            {
                "name": "Cache from Monday close, checked Tuesday pre-market",
                "cache_day": 0,  # Monday
                "cache_hour": 16,
                "cache_minute": 30,
                "check_day": 1,  # Tuesday
                "check_hour": 8,
                "check_minute": 0,
                "expected": True
            },
            {
                "name": "Cache from Monday open, checked Monday after-hours",
                "cache_day": 0,  # Monday
                "cache_hour": 10,
                "cache_minute": 30,
                "check_day": 0,  # Monday
                "check_hour": 17,
                "check_minute": 0,
                "expected": False
            },
            {
                "name": "Cache from Monday after-hours, checked Tuesday pre-market",
                "cache_day": 0,  # Monday
                "cache_hour": 17,
                "cache_minute": 30,
                "check_day": 1,  # Tuesday
                "check_hour": 8,
                "check_minute": 0,
                "expected": True
            },
            
            # Market hours scenarios
            {
                "name": "Cache from 3 minutes ago during market hours",
                "cache_day": 0,  # Monday
                "cache_hour": 10,
                "cache_minute": 30,
                "check_day": 0,  # Monday
                "check_hour": 10,
                "check_minute": 33,
                "market_open": True,
                "expected": True
            },
            {
                "name": "Cache from 7 minutes ago during market hours",
                "cache_day": 0,  # Monday
                "cache_hour": 10,
                "cache_minute": 30,
                "check_day": 0,  # Monday
                "check_hour": 10,
                "check_minute": 37,
                "market_open": True,
                "expected": False
            }
        ]
        
        # Base date for our tests (a Monday)
        base_date = datetime(2025, 4, 14, tzinfo=pytz.timezone('US/Eastern'))
        
        # Test each scenario
        for scenario in scenarios:
            print(f"\nScenario: {scenario['name']}")
            
            # Create cache and check timestamps
            cache_date = base_date + timedelta(days=scenario['cache_day'] - base_date.weekday())
            cache_timestamp = cache_date.replace(
                hour=scenario['cache_hour'], 
                minute=scenario['cache_minute'],
                second=0
            )
            
            check_date = base_date + timedelta(days=scenario['check_day'] - base_date.weekday())
            check_timestamp = check_date.replace(
                hour=scenario['check_hour'], 
                minute=scenario['check_minute'],
                second=0
            )
            
            # Mock the datetime.now function
            class MockDateTime:
                @staticmethod
                def now(tz=None):
                    if tz:
                        return check_timestamp.astimezone(tz)
                    return check_timestamp
            
            # Mock the is_market_open function
            def mock_is_market_open():
                # Check if we specifically set market_open for this scenario
                if "market_open" in scenario:
                    return scenario["market_open"]
                
                # Otherwise calculate based on weekday and time
                if check_timestamp.weekday() > 4:  # Weekend
                    return False
                
                # Check time (9:30am - 4:15pm)
                current_time = check_timestamp.time()
                market_open = time(9, 30, 0)
                market_close = time(16, 15, 0)
                
                return market_open <= current_time <= market_close
            
            # Apply our mocks
            datetime.now = MockDateTime.now
            cache_module.is_market_open = mock_is_market_open
            
            # Test the cache validation
            result = cache_module.should_use_cached_data(cache_timestamp)
            
            print(f"Cache timestamp: {cache_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"Check timestamp: {check_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"Market is {'OPEN' if mock_is_market_open() else 'CLOSED'}")
            print(f"Simulated result: {result}")
            print(f"Expected result: {scenario['expected']}")
            print(f"Test {'PASSED' if result == scenario['expected'] else 'FAILED'}")
    
    finally:
        # Restore original functions
        cache_module.is_market_open = original_is_market_open
        datetime.now = original_datetime_now

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
    test_with_mocked_market_conditions()
    test_live_caching()