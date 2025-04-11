"""
Fix the percentage display for PUT options stop loss recommendations.

This script ensures that the stop loss buffer percentage for PUT options is 
consistently displayed with the correct value (e.g., 1.0% -> 1.0%, not 1.0% -> 5.0%).
"""

def fix_put_stop_loss_percentage():
    """
    Fix the PUT options stop loss percentage display in discord_bot.py
    by ensuring the buffer_percentage is displayed correctly.
    """
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # First, check if we already have a fixed version
    if "# Ensure we're using the correct buffer percentage" in content:
        print("Fix already applied!")
        return
    
    # Find the section where stop_loss_buffer_percentage is determined
    start_section = "# Extract buffer percentage for display in the output"
    end_section = "# Calculate option price at stop loss using delta approximation"
    
    if start_section not in content or end_section not in content:
        print("Error: Could not find the target section to modify")
        return
        
    start_idx = content.find(start_section)
    end_idx = content.find(end_section, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print("Error: Could not find the section boundaries")
        return
    
    current_section = content[start_idx:end_idx]
    
    # Modify the section to fix the percentage display for PUTs
    updated_section = current_section.replace(
        """                else:
                    # For puts, percentage is how far above current price
                    calculated_buffer = abs((stop_loss - current_price) / current_price * 100)
                    # Only use calculated value if we don't have a specific DTE-based value
                    if days_to_expiration > 5:
                        stop_loss_buffer_percentage = calculated_buffer""",
        
        """                else:
                    # For puts, percentage is how far above current price
                    calculated_buffer = abs((stop_loss - current_price) / current_price * 100)
                    # Only use calculated value if we don't have a specific DTE-based value
                    if days_to_expiration > 5:
                        stop_loss_buffer_percentage = calculated_buffer
                
                # Ensure we're using the correct buffer percentage
                if option_type.lower() == 'put':
                    # For puts, always use the fixed buffer percentage based on DTE
                    # so we display 1.0% for 0-1 DTE, 2.0% for 2 DTE, etc.
                    if days_to_expiration <= 1:
                        stop_loss_buffer_percentage = 1.0  # 1% for 0-1 DTE
                    elif days_to_expiration <= 2:
                        stop_loss_buffer_percentage = 2.0  # 2% for 2 DTE
                    elif days_to_expiration <= 5:
                        stop_loss_buffer_percentage = 3.0  # 3% for 3-5 DTE
                    elif days_to_expiration <= 60:
                        stop_loss_buffer_percentage = 5.0  # 5% for medium-term
                    else:
                        stop_loss_buffer_percentage = 7.0  # 7% for long-term"""
    )
    
    # Replace the old section with the updated one
    updated_content = content[:start_idx] + updated_section + content[end_idx:]
    
    # Write the changes back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    print("Successfully fixed PUT options stop loss percentage display!")

if __name__ == "__main__":
    fix_put_stop_loss_percentage()