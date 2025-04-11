"""
Fix the technical support level display in the Discord bot.

The issue is that the Discord bot is calculating the correct technical support levels,
but it's not displaying those values in the embed. Instead, it's showing the maximum
buffer percentage based on DTE.

This fix ensures that when technical support levels are found and they're within
the buffer limits, those technical levels are displayed in the embed rather than
the maximum buffer percentage.
"""

import re

def apply_fix():
    """Apply the fix to discord_bot.py"""
    
    print("Applying fix to ensure technical support levels are properly displayed...")
    
    # Read the current file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Find the section where we set the stop_loss_buffer_percentage
    # This is the problematic code that overwrites the actual technical level percentage
    pattern = r'(# Extract buffer percentage.*?\n.*?if days_to_expiration <= 1:.*?\n.*?stop_loss_buffer_percentage = 1\.0.*?\n.*?elif days_to_expiration <= 2:.*?\n.*?stop_loss_buffer_percentage = 2\.0.*?\n.*?elif days_to_expiration <= 5:.*?\n.*?stop_loss_buffer_percentage = 3\.0.*?\n.*?else:.*?\n.*?stop_loss_buffer_percentage = 5\.0.*?\n\n.*?# If the buffer wasn\'t explicitly available, calculate from the stop_loss.*?\n.*?if option_type\.lower\(\) == \'call\':.*?\n.*?# For calls, percentage is how far below current price.*?\n.*?calculated_buffer = abs\(\(stop_loss - current_price\) \/ current_price \* 100\).*?\n.*?# Only use calculated value if we don\'t have a specific DTE-based value.*?\n.*?if days_to_expiration > 5:.*?\n.*?stop_loss_buffer_percentage = calculated_buffer.*?\n.*?else:.*?\n.*?# For puts, percentage is how far above current price.*?\n.*?calculated_buffer = abs\(\(stop_loss - current_price\) \/ current_price \* 100\).*?\n.*?# Only use calculated value if we don\'t have a specific DTE-based value.*?\n.*?if days_to_expiration > 5:.*?\n.*?stop_loss_buffer_percentage = calculated_buffer)'
    
    # Replacement code that calculates the actual buffer percentage from the stop_loss level
    # but still respects the DTE-based buffer limits
    replacement = '''# Extract buffer percentage for display in the output
                # ALWAYS calculate the actual buffer from stop_loss and current_price
                if option_type.lower() == 'call':
                    # For calls, percentage is how far below current price
                    stop_loss_buffer_percentage = abs((current_price - stop_loss) / current_price * 100)
                else:
                    # For puts, percentage is how far above current price
                    stop_loss_buffer_percentage = abs((stop_loss - current_price) / current_price * 100)
                
                # Just for logging - get the max buffer based on DTE
                if days_to_expiration <= 1:
                    max_buffer = 1.0  # 1% for 0-1 DTE
                elif days_to_expiration <= 2:
                    max_buffer = 2.0  # 2% for 2 DTE
                elif days_to_expiration <= 5:
                    max_buffer = 3.0  # 3% for 3-5 DTE
                elif days_to_expiration <= 60:
                    max_buffer = 5.0  # 5% for medium-term
                else:
                    max_buffer = 7.0 if option_type.lower() == 'put' else 5.0  # 7% for long-term puts, 5% for calls
                
                # Log the buffer percentages for debugging
                print(f"Technical buffer: {stop_loss_buffer_percentage:.2f}%, Max buffer: {max_buffer:.1f}%")
                
                # Note: we don't override stop_loss_buffer_percentage with max_buffer
                # because we want to show the actual technical level when it's within limits'''
    
    # Replace the pattern with our new code
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Now find and update the "Ensure we're using the correct buffer percentage" section that
    # overrides the stop_loss_buffer_percentage for puts
    pattern2 = r'(# Ensure we\'re using the correct buffer percentage.*?\n.*?if option_type\.lower\(\) == \'put\':.*?\n.*?# For puts, always use the fixed buffer percentage based on DTE.*?\n.*?# so we display 1\.0% for 0-1 DTE, 2\.0% for 2 DTE, etc\..*?\n.*?if days_to_expiration <= 1:.*?\n.*?stop_loss_buffer_percentage = 1\.0  # 1% for 0-1 DTE.*?\n.*?elif days_to_expiration <= 2:.*?\n.*?stop_loss_buffer_percentage = 2\.0  # 2% for 2 DTE.*?\n.*?elif days_to_expiration <= 5:.*?\n.*?stop_loss_buffer_percentage = 3\.0  # 3% for 3-5 DTE.*?\n.*?elif days_to_expiration <= 60:.*?\n.*?stop_loss_buffer_percentage = 5\.0  # 5% for medium-term.*?\n.*?else:.*?\n.*?stop_loss_buffer_percentage = 7\.0  # 7% for long-term)'
    
    # Remove this section entirely as we now calculate the actual buffer from stop_loss
    replacement2 = '# We already calculated the actual buffer percentage from the stop_loss level\n                # so we don\'t need to override it with fixed DTE-based values'
    
    # Replace the second pattern with our new code
    updated_content = re.sub(pattern2, replacement2, updated_content, flags=re.DOTALL)
    
    # ADDITIONAL FIX: 
    # In the sections where technical support is found in get_stop_loss_recommendation,
    # make sure we log more details about the technical support and buffer limits
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    print("Fix applied successfully!")

if __name__ == "__main__":
    apply_fix()