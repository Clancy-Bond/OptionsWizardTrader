"""
This script adds dynamic buffer calculations to the longterm stop loss function
in technical_analysis.py. This ensures that even longterm trades have appropriate
buffer sizes based on days to expiration (DTE).
"""

def update_longterm_stop_loss():
    """
    Update the get_longterm_stop_loss function in technical_analysis.py
    to add dynamic buffer calculations based on days to expiration.
    """
    with open('technical_analysis.py', 'r') as file:
        content = file.read()

    # 1. Update the function signature to accept days_to_expiration
    old_signature = "def get_longterm_stop_loss(stock, current_price, option_type):"
    new_signature = "def get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration=None):"
    content = content.replace(old_signature, new_signature)

    # 2. Update the call options section to include dynamic buffer
    old_call_section = """            # Calculate a wider dynamic range based on the ATR over a longer period
            # For elite positions (LEAPS, etc), we need a wider stop to avoid early exit
            stop_loss = current_price - (2.5 * atr)
            
            # Ensure it's not too tight
            max_drop_percentage = 0.12  # 12% maximum drop for long-term
            floor_level = current_price * (1 - max_drop_percentage)"""

    new_call_section = """            # Calculate a wider dynamic range based on the ATR over a longer period
            # For elite positions (LEAPS, etc), we need a wider stop to avoid early exit
            atr_multiple = 2.5  # Default 2.5x ATR
            max_drop_percentage = 0.12  # Default 12% maximum drop for long-term
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 5:
                    atr_multiple = 1.5  # 1.5x ATR for shorter expirations
                    max_drop_percentage = 0.05  # 5% for shorter expirations
                elif days_to_expiration <= 14:
                    atr_multiple = 1.8  # 1.8x ATR for medium-term
                    max_drop_percentage = 0.08  # 8% for medium-term
                elif days_to_expiration <= 30:
                    atr_multiple = 2.0  # 2.0x ATR for longer-term
                    max_drop_percentage = 0.10  # 10% for longer-term
                    
            stop_loss = current_price - (atr_multiple * atr)
            
            # Ensure it's not too tight
            floor_level = current_price * (1 - max_drop_percentage)"""

    content = content.replace(old_call_section, new_call_section)

    # 3. Update the put options section to include dynamic buffer
    old_put_section = """            # Calculate a wider dynamic range based on ATR
            stop_loss = current_price + (2.5 * atr)
            
            # Ensure it's not too tight
            max_rise_percentage = 0.12  # 12% maximum rise for long-term
            ceiling_level = current_price * (1 + max_rise_percentage)"""

    new_put_section = """            # Calculate a wider dynamic range based on ATR
            atr_multiple = 2.5  # Default 2.5x ATR
            max_rise_percentage = 0.12  # Default 12% maximum rise for long-term
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 5:
                    atr_multiple = 1.5  # 1.5x ATR for shorter expirations
                    max_rise_percentage = 0.05  # 5% for shorter expirations
                elif days_to_expiration <= 14:
                    atr_multiple = 1.8  # 1.8x ATR for medium-term
                    max_rise_percentage = 0.08  # 8% for medium-term
                elif days_to_expiration <= 30:
                    atr_multiple = 2.0  # 2.0x ATR for longer-term
                    max_rise_percentage = 0.10  # 10% for longer-term
                    
            stop_loss = current_price + (atr_multiple * atr)
            
            # Ensure it's not too tight
            ceiling_level = current_price * (1 + max_rise_percentage)"""

    content = content.replace(old_put_section, new_put_section)

    # 4. Update the fallback for call options to use dynamic buffer
    old_call_fallback = """        # Fallback to simple percentage based on option type
        if option_type.lower() == 'call':
            stop_loss = current_price * 0.85  # 15% drop for long-term"""

    new_call_fallback = """        # Fallback to simple percentage based on option type
        if option_type.lower() == 'call':
            # Adjust fallback based on days to expiration
            min_percentage = 0.85  # Default 15% drop for long-term
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 5:
                    min_percentage = 0.95  # 5% for shorter expirations
                elif days_to_expiration <= 14:
                    min_percentage = 0.92  # 8% for medium-term
                elif days_to_expiration <= 30:
                    min_percentage = 0.90  # 10% for longer-term
                    
            stop_loss = current_price * min_percentage"""

    content = content.replace(old_call_fallback, new_call_fallback)

    # 5. Update the fallback for put options to use dynamic buffer
    old_put_fallback = """        else:
            stop_loss = current_price * 1.15  # 15% rise for long-term"""

    new_put_fallback = """        else:
            # Adjust fallback based on days to expiration
            max_percentage = 1.15  # Default 15% rise for long-term
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 5:
                    max_percentage = 1.05  # 5% for shorter expirations
                elif days_to_expiration <= 14:
                    max_percentage = 1.08  # 8% for medium-term
                elif days_to_expiration <= 30:
                    max_percentage = 1.10  # 10% for longer-term
                    
            stop_loss = current_price * max_percentage"""

    content = content.replace(old_put_fallback, new_put_fallback)
    
    # 6. Update the fallback return strings to show dynamic percentages
    old_call_return = """            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} (15% below current price)\\n• Conservative long-term protection level",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5"""
                
    new_call_return = """            # Calculate percentage drop for display
            percentage_drop = ((current_price - stop_loss) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\\n• Conservative long-term protection level",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5"""
                
    content = content.replace(old_call_return, new_call_return)
    
    old_put_return = """            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} (15% above current price)\\n• Conservative long-term protection level",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5"""
                
    new_put_return = """            # Calculate percentage rise for display
            percentage_rise = ((stop_loss - current_price) / current_price) * 100
            
            return {
                "level": stop_loss,
                "recommendation": f"🌟 **LONG-TERM TRADE STOP LOSS (Weekly chart)** 🌟\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\\n• Conservative long-term protection level",
                "time_horizon": "longterm",
                "option_stop_price": current_price * 0.5"""
                
    content = content.replace(old_put_return, new_put_return)

    # 7. Update the get_stop_loss_recommendation function to pass days_to_expiration to get_longterm_stop_loss
    old_function_call = "        longterm_recommendation = get_longterm_stop_loss(stock, current_price, option_type)"
    new_function_call = "        longterm_recommendation = get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration)"
    content = content.replace(old_function_call, new_function_call)

    # Write the updated content back to the file
    with open('technical_analysis.py', 'w') as file:
        file.write(content)

    print("Updated get_longterm_stop_loss function to use dynamic buffers based on days to expiration.")

if __name__ == "__main__":
    update_longterm_stop_loss()