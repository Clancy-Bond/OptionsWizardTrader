"""
Modified version of enforce_buffer_limits that returns additional information
about whether buffer limits were enforced.
"""

def enforce_buffer_limits(self, stop_loss, current_price, option_type, days_to_expiration):
    """
    Enforces buffer limits on stop loss levels.
    
    Returns:
        tuple: (adjusted_stop_loss, max_buffer_percentage, enforced)
        where enforced is a boolean indicating if the limit was enforced
    """
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
            
        # Calculate how much we're adjusting the stop loss by
        adjustment_percentage = abs(adjusted_stop_loss - stop_loss) / current_price * 100
        
        # Only log if adjustment is significant (greater than 0.01%)
        if adjustment_percentage > 0.01:
            print(f"Adjusting stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE")
            print(f"Current price: ${current_price:.2f}, adjustment amount: {adjustment_percentage:.2f}% of price")
        
        # Return adjusted stop loss and flag that enforcement was applied
        return adjusted_stop_loss, max_buffer_percentage, True
    else:
        # Current buffer is within limits, no need to adjust
        # Return original stop loss and flag that no enforcement was needed
        return stop_loss, max_buffer_percentage, False