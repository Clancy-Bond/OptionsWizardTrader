"""
Test script for verifying the fixed technical support level display.
This directly tests the discord_bot.py's enforce_buffer_limits method.
"""

from discord_bot import OptionsBot

def test_enforce_buffer_limits():
    """Test the fixed enforce_buffer_limits method"""
    
    # Create a bot instance
    bot = OptionsBot()
    
    print("===== Testing TSLA CALL 24 DTE (should show technical support) =====")
    # Test case 1: TSLA call with 24 DTE
    # Technical support at 217.02 (2.18% buffer) - should NOT be enforced since < 5%
    current_price = 221.86
    technical_stop = 217.02  # Technical support (2.18% below current)
    option_type = "call"
    days_to_expiration = 24
    
    # Test the method
    result, max_buffer, enforced = bot.enforce_buffer_limits(
        technical_stop, current_price, option_type, days_to_expiration
    )
    
    # Calculate actual buffer
    actual_buffer = (current_price - result) / current_price * 100
    
    print(f"Technical stop: ${technical_stop:.2f} ({(current_price - technical_stop) / current_price * 100:.2f}% buffer)")
    print(f"Max buffer allowed: {max_buffer:.1f}%")
    print(f"Result stop: ${result:.2f} ({actual_buffer:.2f}% buffer)")
    print(f"Buffer enforced: {enforced}")
    print(f"Expected behavior: Should NOT enforce buffer limit (technical level < max)")
    print(f"Actual behavior: {'CORRECT - used technical level' if not enforced else 'ERROR - used max buffer'}")
    print()
    
    print("===== Testing SPY PUT 5 DTE (should enforce max buffer) =====")
    # Test case 2: SPY put with 5 DTE
    # Technical resistance at 567.42 (14.29% buffer) - should be enforced to 3%
    current_price = 496.48
    technical_stop = 567.42  # Technical resistance (14.29% above current)
    option_type = "put"
    days_to_expiration = 5
    
    # Test the method
    result, max_buffer, enforced = bot.enforce_buffer_limits(
        technical_stop, current_price, option_type, days_to_expiration
    )
    
    # Calculate actual buffer
    actual_buffer = (result - current_price) / current_price * 100
    
    print(f"Technical stop: ${technical_stop:.2f} ({(technical_stop - current_price) / current_price * 100:.2f}% buffer)")
    print(f"Max buffer allowed: {max_buffer:.1f}%")
    print(f"Result stop: ${result:.2f} ({actual_buffer:.2f}% buffer)")
    print(f"Buffer enforced: {enforced}")
    print(f"Expected behavior: Should enforce buffer limit (technical level > max)")
    print(f"Actual behavior: {'CORRECT - enforced max buffer' if enforced else 'ERROR - used technical level'}")
    print()

if __name__ == "__main__":
    test_enforce_buffer_limits()