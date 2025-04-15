"""
Test the moneyness detection functionality to ensure it works correctly
for both call and put options.
"""
from polygon_integration import determine_moneyness

def test_moneyness():
    # Test call options
    print("Testing CALL options:")
    print(f"Strike 100, Stock 120: {determine_moneyness(100, 120, 'call')}")  # Should be in-the-money
    print(f"Strike 150, Stock 120: {determine_moneyness(150, 120, 'call')}")  # Should be out-of-the-money
    
    # Test put options
    print("\nTesting PUT options:")
    print(f"Strike 150, Stock 120: {determine_moneyness(150, 120, 'put')}")   # Should be in-the-money
    print(f"Strike 100, Stock 120: {determine_moneyness(100, 120, 'put')}")   # Should be out-of-the-money
    
    # Test with string inputs
    print("\nTesting string inputs:")
    print(f"Strike '100', Stock 120: {determine_moneyness('100', 120, 'call')}")  # Should be in-the-money
    
    # Test edge cases
    print("\nTesting edge cases:")
    print(f"Invalid strike: {determine_moneyness('invalid', 120, 'call')}")  # Should default to in-the-money
    print(f"Stock price 0: {determine_moneyness(100, 0, 'put')}")            # Should be in-the-money for put

if __name__ == "__main__":
    test_moneyness()