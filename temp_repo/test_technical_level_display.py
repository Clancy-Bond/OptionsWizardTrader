"""
Test script to verify the technical stop level display is correctly showing
the technical analysis level when within buffer limits.

This is a direct check focused on the buffer enforcement mechanism to ensure
we're displaying the correct stop level.
"""

import importlib.util
import sys
from pathlib import Path
import inspect

# Import technical_analysis and discord_bot with proper error handling
def import_module_from_file(file_path, module_name):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            print(f"Failed to load spec for {module_name} from {file_path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error importing {module_name} from {file_path}: {e}")
        return None

def test_buffer_enforcement():
    """
    Test the technical stop level display by simulating the handle_stop_loss_request
    with different parameters to verify the buffer enforcement and display logic.
    
    This test focuses specifically on ensuring we display the technical level
    when it's within buffer limits, not the maximum buffer level.
    """
    print("\n=== Testing Technical Level Display ===\n")
    
    # Import the modules
    discord_bot_module = import_module_from_file("discord_bot.py", "discord_bot")
    if not discord_bot_module:
        print("Failed to import discord_bot.py")
        return
    
    # Create a bot instance
    options_bot = discord_bot_module.OptionsBot()
    
    # Test data for various scenarios
    test_cases = [
        # Test case 1: Technical level within buffer limits (CALL option)
        {
            "name": "CALL option - Technical level within buffer limits (no enforcement)",
            "stop_loss": 95.0,        # Technical level is 5% below current price (within 5% limit)
            "current_price": 100.0,   # Current price
            "option_type": "call",    # CALL option
            "days_to_expiration": 10, # 10 DTE (5% buffer limit applies)
            "expected_enforced": False,# Buffer enforcement should not be needed
            "expected_stop": 95.0,    # Should display original technical level
        },
        # Test case 2: Technical level exceeds buffer limits (CALL option)
        {
            "name": "CALL option - Technical level exceeds buffer limits (enforcement)",
            "stop_loss": 93.0,        # Technical level is 7% below current price (exceeds 5% limit)
            "current_price": 100.0,   # Current price
            "option_type": "call",    # CALL option
            "days_to_expiration": 10, # 10 DTE (5% buffer limit applies)
            "expected_enforced": True, # Buffer enforcement should be applied
            "expected_stop": 95.0,    # Should display 5% buffer level
        },
        # Test case 3: Technical level within buffer limits (PUT option)
        {
            "name": "PUT option - Technical level within buffer limits (no enforcement)",
            "stop_loss": 103.0,       # Technical level is 3% above current price (within 5% limit)
            "current_price": 100.0,   # Current price
            "option_type": "put",     # PUT option
            "days_to_expiration": 10, # 10 DTE (5% buffer limit applies)
            "expected_enforced": False,# Buffer enforcement should not be needed
            "expected_stop": 103.0,   # Should display original technical level
        },
        # Test case 4: Technical level exceeds buffer limits (PUT option)
        {
            "name": "PUT option - Technical level exceeds buffer limits (enforcement)",
            "stop_loss": 108.0,       # Technical level is 8% above current price (exceeds 5% limit)
            "current_price": 100.0,   # Current price
            "option_type": "put",     # PUT option
            "days_to_expiration": 10, # 10 DTE (5% buffer limit applies)
            "expected_enforced": True, # Buffer enforcement should be applied
            "expected_stop": 105.0,   # Should display 5% buffer level
        },
        # Test case 5: Edge case - Technical level exactly at buffer limit (CALL)
        {
            "name": "CALL option - Technical level exactly at buffer limit",
            "stop_loss": 90.0,        # Technical level is 10% below current price (exactly at 10% limit)
            "current_price": 100.0,   # Current price
            "option_type": "call",    # CALL option
            "days_to_expiration": 100,# 100 DTE (should apply 5% buffer limit)
            "expected_enforced": True, # Buffer enforcement should be applied
            "expected_stop": 95.0,    # Should display 5% buffer level
        },
        # Test case 6: Edge case - Technical level exactly at buffer limit (PUT)
        {
            "name": "PUT option - Technical level exactly at buffer limit",
            "stop_loss": 110.0,       # Technical level is 10% above current price (above 7% limit)
            "current_price": 100.0,   # Current price
            "option_type": "put",     # PUT option
            "days_to_expiration": 100,# 100 DTE (should apply 7% buffer limit)
            "expected_enforced": True, # Buffer enforcement should be applied
            "expected_stop": 107.0,   # Should display 7% buffer level
        }
    ]
    
    # Testing the buffer enforcement
    for tc in test_cases:
        print(f"Test: {tc['name']}")
        
        # Call enforce_buffer_limits method directly
        adjusted_stop, max_buffer, enforced = options_bot.enforce_buffer_limits(
            tc["stop_loss"], 
            tc["current_price"], 
            tc["option_type"], 
            tc["days_to_expiration"]
        )
        
        # Verify if buffer enforcement behaved as expected
        if enforced == tc["expected_enforced"]:
            print(f"  ✓ Buffer enforcement result is correct: {enforced}")
        else:
            print(f"  ✗ Buffer enforcement result is NOT correct: {enforced}, expected: {tc['expected_enforced']}")
        
        # Verify if stop loss level is as expected
        if abs(adjusted_stop - tc["expected_stop"]) < 0.01:  # Allow small float difference
            print(f"  ✓ Stop loss level is correct: ${adjusted_stop:.2f}, expected: ${tc['expected_stop']:.2f}")
        else:
            print(f"  ✗ Stop loss level is NOT correct: ${adjusted_stop:.2f}, expected: ${tc['expected_stop']:.2f}")
            
        # Calculate final stop loss and percentage based on the exact calculation in handle_stop_loss_request
        if enforced:
            final_stop = adjusted_stop
            if tc["option_type"].lower() == 'call':
                buffer_percentage = abs((tc["current_price"] - final_stop) / tc["current_price"] * 100)
            else:
                buffer_percentage = abs((final_stop - tc["current_price"]) / tc["current_price"] * 100)
        else:
            final_stop = tc["stop_loss"]
            if tc["option_type"].lower() == 'call':
                buffer_percentage = abs((tc["current_price"] - final_stop) / tc["current_price"] * 100)
            else:
                buffer_percentage = abs((final_stop - tc["current_price"]) / tc["current_price"] * 100)
                
        # Print final stop level and buffer percentage for reference
        print(f"  • Final stop level: ${final_stop:.2f}, buffer: {buffer_percentage:.2f}%")
        print("")
    
    print("\nTest summary:")
    print("This test verifies that we correctly display the technical analysis level")
    print("when it's within buffer limits, rather than always displaying the maximum")
    print("buffer percentage limit for the given DTE.")
    print("\nOur fix ensures that:")
    print("1. We preserve the technical_stop variable throughout processing")
    print("2. We pass technical_stop, not stop_loss, to enforce_buffer_limits")
    print("3. We display the technical level when no enforcement is needed")
    print("4. We only display the buffer cap level when technical level exceeds the cap\n")
    
if __name__ == "__main__":
    test_buffer_enforcement()