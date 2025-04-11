"""
Direct test script to verify the enforce_buffer_limits method works correctly.
This test verifies that enforcement only happens when technical levels exceed limits.
"""
import importlib.util
import sys

# Import discord_bot.py as a module 
def import_module_from_file(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import discord_bot
discord_bot = import_module_from_file("discord_bot.py", "discord_bot")

def test_enforce_buffer_limits():
    """Test the enforce_buffer_limits method directly with various technical levels"""
    # Create an instance of OptionsBot
    bot = discord_bot.OptionsBot()
    
    # We'll test with a fixed current price
    current_price = 100.0
    
    # Test all combinations:
    # - CALL and PUT options
    # - Various DTE values (1, 2, 5, 30, 90)
    # - Technical levels both within and exceeding buffer limits
    test_scenarios = [
        # Structure: (option_type, days_to_expiration, technical_level_pct, should_enforce)
        
        # CALL OPTIONS - Within buffer limits
        ('call', 1, 0.5, False),    # 0.5% < 1% limit
        ('call', 2, 1.8, False),    # 1.8% < 2% limit
        ('call', 5, 2.5, False),    # 2.5% < 3% limit
        ('call', 30, 4.5, False),   # 4.5% < 5% limit
        ('call', 90, 4.8, False),   # 4.8% < 5% limit (long-term)
        
        # CALL OPTIONS - Exceeding buffer limits
        ('call', 1, 1.5, True),     # 1.5% > 1% limit
        ('call', 2, 2.5, True),     # 2.5% > 2% limit
        ('call', 5, 3.5, True),     # 3.5% > 3% limit
        ('call', 30, 5.5, True),    # 5.5% > 5% limit
        ('call', 90, 5.2, True),    # 5.2% > 5% limit (long-term)
        
        # PUT OPTIONS - Within buffer limits
        ('put', 1, 0.5, False),     # 0.5% < 1% limit
        ('put', 2, 1.8, False),     # 1.8% < 2% limit
        ('put', 5, 2.5, False),     # 2.5% < 3% limit 
        ('put', 30, 4.5, False),    # 4.5% < 5% limit
        ('put', 90, 6.5, False),    # 6.5% < 7% limit (long-term)
        
        # PUT OPTIONS - Exceeding buffer limits
        ('put', 1, 1.5, True),      # 1.5% > 1% limit
        ('put', 2, 2.5, True),      # 2.5% > 2% limit
        ('put', 5, 3.5, True),      # 3.5% > 3% limit
        ('put', 30, 5.5, True),     # 5.5% > 5% limit
        ('put', 90, 7.5, True),     # 7.5% > 7% limit (long-term)
    ]
    
    # Run all test scenarios
    for scenario in test_scenarios:
        option_type, days_to_expiration, technical_pct, should_enforce = scenario
        
        # Calculate the technical stop loss level based on percentage
        if option_type == 'call':
            technical_stop = current_price * (1 - technical_pct/100)  # Percentage below
        else:
            technical_stop = current_price * (1 + technical_pct/100)  # Percentage above
        
        # Get the correct buffer limit percentage based on DTE
        if days_to_expiration <= 1:
            buffer_limit = 1.0
        elif days_to_expiration <= 2:
            buffer_limit = 2.0
        elif days_to_expiration <= 5:
            buffer_limit = 3.0
        elif days_to_expiration <= 60:
            buffer_limit = 5.0
        else:
            buffer_limit = 7.0 if option_type == 'put' else 5.0
        
        # Calculate what the buffer stop would be
        if option_type == 'call':
            buffer_stop = current_price * (1 - buffer_limit/100)
        else:
            buffer_stop = current_price * (1 + buffer_limit/100)
        
        # Call enforce_buffer_limits
        adjusted_stop, max_buffer, enforced = bot.enforce_buffer_limits(
            technical_stop, current_price, option_type, days_to_expiration)
        
        # Print the results
        print(f"\nTesting {option_type.upper()} with {days_to_expiration} DTE:")
        print(f"  Technical stop: ${technical_stop:.2f} ({technical_pct:.1f}% {'below' if option_type == 'call' else 'above'} current price)")
        print(f"  Buffer limit:   ${buffer_stop:.2f} ({buffer_limit:.1f}% {'below' if option_type == 'call' else 'above'} current price)")
        print(f"  Adjusted stop:  ${adjusted_stop:.2f}")
        print(f"  Max buffer:     {max_buffer:.1f}%")
        print(f"  Buffer enforced: {enforced}")
        
        # Verify the result
        if should_enforce:
            if enforced:
                print(f"  ✅ PASS: Buffer enforcement activated as expected")
                # Check if the adjusted stop is at the buffer limit
                if abs(adjusted_stop - buffer_stop) < 0.01:
                    print(f"  ✅ PASS: Stop correctly adjusted to buffer limit")
                else:
                    print(f"  ❌ FAIL: Stop not correctly adjusted to buffer limit")
            else:
                print(f"  ❌ FAIL: Buffer should have been enforced but wasn't")
        else:
            if not enforced:
                print(f"  ✅ PASS: No buffer enforcement as expected")
                # Check if original technical stop is preserved
                if abs(adjusted_stop - technical_stop) < 0.01:
                    print(f"  ✅ PASS: Technical stop correctly preserved")
                else:
                    print(f"  ❌ FAIL: Technical stop not correctly preserved")
            else:
                print(f"  ❌ FAIL: Buffer enforced but shouldn't have been")

if __name__ == "__main__":
    print("===== TESTING BUFFER ENFORCEMENT =====")
    print("This test verifies that the enforce_buffer_limits method only")
    print("applies enforcement when technical levels exceed buffer limits")
    
    test_enforce_buffer_limits()
    
    print("\n===== TEST COMPLETE =====")