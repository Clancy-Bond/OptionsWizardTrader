"""
Test script to verify our buffer fix works correctly for both CALL and PUT options.
This will test the fixes in enforce_buffer_limits in discord_bot.py.
"""
import sys
import importlib.util

# Import discord_bot.py as a module
spec = importlib.util.spec_from_file_location("discord_bot", "discord_bot.py")
discord_bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discord_bot)

def test_buffer_limits_calls():
    """Test buffer limits for CALL options with different DTE values"""
    print("\n===== TESTING CALL OPTIONS =====")
    
    # Create an instance of OptionsBot
    bot = discord_bot.OptionsBot()
    
    # Test cases for CALL options
    option_type = 'call'
    current_price = 100.0  # Current stock price $100
    
    # For each DTE value, we'll test:
    # 1. A stop loss within the buffer limits (should not be enforced)
    # 2. A stop loss outside the buffer limits (should be enforced)
    
    # Case 1: 0-1 DTE (1% buffer)
    print("\n----- 1 DTE CALL (1% buffer) -----")
    days_to_expiration = 1
    
    # Test when stop loss is within buffer (above min)
    stop_loss = 99.5  # 0.5% drop, within 1% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (0.5% below current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer (below min)
    stop_loss = 98.5  # 1.5% drop, outside 1% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (1.5% below current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Case 2: 2 DTE (2% buffer)
    print("\n----- 2 DTE CALL (2% buffer) -----")
    days_to_expiration = 2
    
    # Test when stop loss is within buffer
    stop_loss = 98.5  # 1.5% drop, within 2% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (1.5% below current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer
    stop_loss = 97.5  # 2.5% drop, outside 2% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (2.5% below current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Case 3: 5 DTE (3% buffer)
    print("\n----- 5 DTE CALL (3% buffer) -----")
    days_to_expiration = 5
    
    # Test when stop loss is within buffer
    stop_loss = 97.5  # 2.5% drop, within 3% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (2.5% below current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer
    stop_loss = 96.5  # 3.5% drop, outside 3% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (3.5% below current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Case 4: 30 DTE (5% buffer)
    print("\n----- 30 DTE CALL (5% buffer) -----")
    days_to_expiration = 30
    
    # Test when stop loss is within buffer
    stop_loss = 96.0  # 4% drop, within 5% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (4.0% below current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer
    stop_loss = 94.0  # 6% drop, outside 5% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (6.0% below current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")

def test_buffer_limits_puts():
    """Test buffer limits for PUT options with different DTE values"""
    print("\n===== TESTING PUT OPTIONS =====")
    
    # Create an instance of OptionsBot
    bot = discord_bot.OptionsBot()
    
    # Test cases for PUT options
    option_type = 'put'
    current_price = 100.0  # Current stock price $100
    
    # For each DTE value, we'll test:
    # 1. A stop loss within the buffer limits (should not be enforced)
    # 2. A stop loss outside the buffer limits (should be enforced)
    
    # Case 1: 0-1 DTE (1% buffer)
    print("\n----- 1 DTE PUT (1% buffer) -----")
    days_to_expiration = 1
    
    # Test when stop loss is within buffer (below max)
    stop_loss = 100.5  # 0.5% rise, within 1% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (0.5% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer (above max)
    stop_loss = 101.5  # 1.5% rise, outside 1% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (1.5% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Case 2: 2 DTE (2% buffer)
    print("\n----- 2 DTE PUT (2% buffer) -----")
    days_to_expiration = 2
    
    # Test when stop loss is within buffer
    stop_loss = 101.5  # 1.5% rise, within 2% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (1.5% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer
    stop_loss = 102.5  # 2.5% rise, outside 2% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (2.5% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Case 3: 5 DTE (3% buffer)
    print("\n----- 5 DTE PUT (3% buffer) -----")
    days_to_expiration = 5
    
    # Test when stop loss is within buffer
    stop_loss = 102.5  # 2.5% rise, within 3% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (2.5% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer
    stop_loss = 103.5  # 3.5% rise, outside 3% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (3.5% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Case 4: 30 DTE (5% buffer)
    print("\n----- 30 DTE PUT (5% buffer) -----")
    days_to_expiration = 30
    
    # Test when stop loss is within buffer
    stop_loss = 104.0  # 4% rise, within 5% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (4.0% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer
    stop_loss = 106.0  # 6% rise, outside 5% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (6.0% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Case 5: 90 DTE (7% buffer for puts)
    print("\n----- 90 DTE PUT (7% buffer) -----")
    days_to_expiration = 90
    
    # Test when stop loss is within buffer
    stop_loss = 106.0  # 6% rise, within 7% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (6.0% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")
    
    # Test when stop loss is outside buffer
    stop_loss = 108.0  # 8% rise, outside 7% buffer
    adjusted_stop_loss, max_buffer, enforced = bot.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
    print(f"Stop loss: ${stop_loss:.2f} (8.0% above current price)")
    print(f"Adjusted: ${adjusted_stop_loss:.2f}, Max buffer: {max_buffer:.1f}%, Enforced: {enforced}")

if __name__ == "__main__":
    print("===== TESTING BUFFER LIMIT ENFORCEMENT =====")
    print("This will verify that the enforce_buffer_limits method is working correctly")
    print("It will test both CALL and PUT options with various DTE values")
    print("The buffer should only be enforced when stop loss exceeds the max buffer")
    
    test_buffer_limits_calls()
    test_buffer_limits_puts()
    
    print("\n===== TEST COMPLETE =====")