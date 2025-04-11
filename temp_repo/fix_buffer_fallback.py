"""
Fix the buffer fallback mechanism in the discord bot stop loss recommendations.

This script modifies discord_bot.py to ensure it always enforces DTE-based
buffer limitations when the technical analysis method produces stop loss 
recommendations that exceed these limitations.
"""

def apply_buffer_fallback_fix():
    """
    Apply fixes to ensure the bot properly falls back to DTE-based buffers
    when technical analysis produces values outside accepted ranges.
    """
    with open('discord_bot.py', 'r') as file:
        content = file.read()

    # Add a new function to enforce buffer limits based on DTE
    enforcement_function = """
    def enforce_buffer_limits(self, stop_loss, current_price, option_type, days_to_expiration):
        \"\"\"
        Enforce buffer limitations based on days to expiration.
        This ensures stop loss levels don't exceed appropriate buffers for the trade duration.
        
        Args:
            stop_loss: Calculated stop loss level
            current_price: Current stock price
            option_type: 'call' or 'put'
            days_to_expiration: Days until option expiration
            
        Returns:
            Adjusted stop loss level that respects DTE-based buffer limits
        \"\"\"
        # Calculate the current buffer percentage from the given stop_loss
        if option_type.lower() == 'call':
            # For calls, buffer is how far below current price
            current_buffer_percentage = (current_price - stop_loss) / current_price * 100
        else:
            # For puts, buffer is how far above current price
            current_buffer_percentage = (stop_loss - current_price) / current_price * 100
            
        # Determine the maximum allowed buffer based on DTE
        if days_to_expiration <= 1:
            max_buffer_percentage = 1.0  # 1% for 0-1 DTE
        elif days_to_expiration <= 2:
            max_buffer_percentage = 2.0  # 2% for 2 DTE
        elif days_to_expiration <= 5:
            max_buffer_percentage = 3.0  # 3% for 3-5 DTE
        elif days_to_expiration <= 60:
            max_buffer_percentage = 5.0  # 5% for medium-term
        else:
            max_buffer_percentage = 7.0 if option_type.lower() == 'put' else 5.0  # 7% for long-term puts, 5% for calls
            
        # Check if current buffer exceeds the maximum allowed
        if current_buffer_percentage > max_buffer_percentage:
            # Apply the maximum allowed buffer instead
            if option_type.lower() == 'call':
                # For calls, stop loss is below current price
                adjusted_stop_loss = current_price * (1 - max_buffer_percentage/100)
            else:
                # For puts, stop loss is above current price
                adjusted_stop_loss = current_price * (1 + max_buffer_percentage/100)
                
            print(f"Adjusting stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE")
            return adjusted_stop_loss
            
        # If current buffer is within limits, return original stop loss
        return stop_loss
    """
    
    # Insert the new function after the OptionsBot class definition
    content = content.replace("class OptionsBot:", f"class OptionsBot:\n{enforcement_function}")
    
    # Update the async handle_stop_loss_request method to call our new function
    # Find where stop_loss is extracted from stop_loss_data
    stop_loss_extraction = "stop_loss = stop_loss_data.get(\"level\", current_price * 0.95 if option_type == \"call\" else current_price * 1.05)"
    
    # Add the enforcement call after that line
    updated_stop_loss_extraction = stop_loss_extraction + "\n                \n                # Enforce buffer limitations based on DTE\n                stop_loss = self.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)"
    
    content = content.replace(stop_loss_extraction, updated_stop_loss_extraction)
    
    # Save the updated file
    with open('discord_bot.py', 'w') as file:
        file.write(content)
        
    print("Buffer fallback fix applied successfully.")
    
if __name__ == "__main__":
    apply_buffer_fallback_fix()