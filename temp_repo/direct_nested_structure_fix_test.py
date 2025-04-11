"""
Direct test of the nested structure fix for stop loss data handling.
Focuses specifically on the issue where the stop_loss_data dictionary 
returns nested structures from get_stop_loss_recommendations().
"""

import os
import sys
import importlib.util
from datetime import datetime
import traceback

def import_module_from_file(file_path, module_name):
    """Import a module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def simulate_nested_result_handling():
    """
    Direct test of the fix by simulating a nested data structure from get_stop_loss_recommendations
    """
    # Import our bot module
    try:
        bot_module = import_module_from_file('discord_bot.py', 'discord_bot')
        
        # Create a test bot instance
        bot = bot_module.OptionsBot()
        
        # TSLA example
        current_price = 221.86
        
        # Test case 1: Nested swing structure (within buffer limits)
        nested_swing_data = {
            'trade_horizon': 'swing',
            'swing': {
                'level': 217.02,
                'recommendation': 'Use the swing level',
                'time_horizon': 'swing'
            }
        }
        
        # Test case 2: Flat structure (within buffer limits)
        flat_data = {
            'trade_horizon': 'swing',
            'level': 216.50,
            'recommendation': 'Use the flat level',
            'time_horizon': 'swing'
        }
        
        # Test case 3: Primary nested structure (within buffer limits)
        nested_primary_data = {
            'trade_horizon': 'swing',
            'primary': {
                'level': 215.80,
                'recommendation': 'Use the primary level'
            }
        }
        
        # Test case 4: Nested structure (exceeds buffer limits)
        exceeds_buffer_swing = {
            'trade_horizon': 'swing',
            'swing': {
                'level': 195.20, # Far below current price (11.6% drop)
                'recommendation': 'This level exceeds max buffer limit',
                'time_horizon': 'swing'
            }
        }
        
        # Test case 5: Flat structure with PUT (exceeds buffer limits)
        exceeds_buffer_put = {
            'trade_horizon': 'swing',
            'level': 255.30, # Far above current price (15.1% rise)
            'recommendation': 'This PUT level exceeds max buffer limit',
            'time_horizon': 'swing'
        }
        
        test_cases = [
            ("Nested swing structure (within limits)", nested_swing_data, 'call', 23),
            ("Flat structure (within limits)", flat_data, 'call', 23),
            ("Nested primary structure (within limits)", nested_primary_data, 'call', 23),
            ("Exceeds buffer swing structure", exceeds_buffer_swing, 'call', 23),
            ("Exceeds buffer PUT case", exceeds_buffer_put, 'put', 23),
        ]
        
        # Test each case
        for name, data, option_type, dte in test_cases:
            print(f"\n===== Testing {name} =====")
            
            # Extract the technical stop level using our fixed approach
            technical_stop = None
            if "level" in data:
                technical_stop = data.get("level")
                print(f"Found technical stop level {technical_stop} in direct level key")
            elif data.get("swing") and "level" in data.get("swing", {}):
                technical_stop = data.get("swing", {}).get("level")
                print(f"Found technical stop level {technical_stop} in swing nested structure")
            elif data.get("primary") and "level" in data.get("primary", {}):
                technical_stop = data.get("primary", {}).get("level")
                print(f"Found technical stop level {technical_stop} in primary nested structure")
                
            if technical_stop is None:
                print("No technical stop level found in the data!")
                continue
                
            # Now test our buffer enforcement with this technical stop
            try:
                # Run through the buffer enforcement logic
                print(f"Testing with technical_stop={technical_stop}, current_price={current_price}")
                adjusted_stop, max_buffer, enforced = bot.enforce_buffer_limits(
                    technical_stop, current_price, option_type, dte
                )
                
                # Calculate buffer percentage for display
                if option_type.lower() == 'call':
                    # For calls, percentage is how far below current price
                    buffer_percentage = abs((current_price - technical_stop) / current_price * 100)
                else:
                    # For puts, percentage is how far above current price
                    buffer_percentage = abs((technical_stop - current_price) / current_price * 100)
                    
                print(f"Technical buffer percentage: {buffer_percentage:.2f}%")
                print(f"Maximum allowed buffer: {max_buffer:.2f}%")
                print(f"Buffer was enforced: {enforced}")
                print(f"Final stop loss to display: ${adjusted_stop:.2f}")
                
                # Test the display logic too
                stop_loss = technical_stop
                if enforced:
                    stop_loss = adjusted_stop
                    stop_loss_buffer_percentage = max_buffer
                else:
                    stop_loss_buffer_percentage = buffer_percentage
                    
                print(f"Final display variables:")
                print(f"  stop_loss = ${stop_loss:.2f}")
                print(f"  stop_loss_buffer_percentage = {stop_loss_buffer_percentage:.2f}%")
                print(f"Example display: Stock Price Stop Level: ${stop_loss:.2f} ({stop_loss_buffer_percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)")
                
            except Exception as e:
                print(f"Error in enforcement test: {e}")
                traceback.print_exc()
        
    except Exception as e:
        print(f"Error in test: {e}")
        traceback.print_exc()
        
def main():
    print("==== TESTING NESTED STRUCTURE FIX FOR STOP LOSS DATA ====")
    simulate_nested_result_handling()
        
if __name__ == "__main__":
    main()