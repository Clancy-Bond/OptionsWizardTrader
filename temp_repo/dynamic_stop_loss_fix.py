"""
This script modifies the swing and scalp stop loss calculations to use dynamic buffers 
based on days to expiration (DTE).

For very short-term options (1-2 days), the buffer will be much smaller (1-2%)
than for longer-term options (up to 5%).

The main fixes are in the get_scalp_stop_loss and get_swing_stop_loss functions.
"""

def apply_dynamic_stop_loss_fix():
    """
    Apply the dynamic stop loss buffer fix to technical_analysis.py.
    This will modify the swing and scalp trade stop loss calculations
    to use a buffer that scales based on days to expiration.
    """
    import re
    
    # Read the current technical_analysis.py file
    with open('technical_analysis.py', 'r') as file:
        content = file.read()
    
    # First, modify the get_stop_loss_recommendation function to pass days to expiration 
    # to get_scalp_stop_loss and get_swing_stop_loss
    scalp_call_pattern = r'scalp_recommendation = get_scalp_stop_loss\(stock, current_price, option_type\)'
    scalp_replacement = 'scalp_recommendation = get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration)'
    
    swing_call_pattern = r'swing_recommendation = get_swing_stop_loss\(stock, current_price, option_type\)'
    swing_replacement = 'swing_recommendation = get_swing_stop_loss(stock, current_price, option_type, days_to_expiration)'
    
    # Update the function calls
    content = re.sub(scalp_call_pattern, scalp_replacement, content)
    content = re.sub(swing_call_pattern, swing_replacement, content)
    
    # Now update the function definitions to accept days_to_expiration parameter
    scalp_def_pattern = r'def get_scalp_stop_loss\(stock, current_price, option_type\):'
    scalp_def_replacement = 'def get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration=None):'
    
    swing_def_pattern = r'def get_swing_stop_loss\(stock, current_price, option_type\):'
    swing_def_replacement = 'def get_swing_stop_loss(stock, current_price, option_type, days_to_expiration=None):'
    
    content = re.sub(scalp_def_pattern, scalp_def_replacement, content)
    content = re.sub(swing_def_pattern, swing_def_replacement, content)
    
    # Now modify the PUT option buffer in the scalp function
    # This section is for SCALP trades (PUT options)
    scalp_put_buffer_pattern = r'stop_loss = breakdown_high \+ \(0\.1 \* atr\)'
    
    scalp_put_buffer_replacement = """# Calculate dynamic buffer based on days to expiration
            buffer_factor = 0.1  # Default buffer factor
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 1:
                    buffer_factor = 0.05  # Half the buffer for 0-1 DTE
                elif days_to_expiration <= 2:
                    buffer_factor = 0.07  # 70% of normal buffer for 2 DTE
            
            stop_loss = breakdown_high + (buffer_factor * atr)"""
    
    content = re.sub(scalp_put_buffer_pattern, scalp_put_buffer_replacement, content)
    
    # Modify the CALL option buffer in the scalp function for consistency
    scalp_call_buffer_pattern = r'stop_loss = breakout_low - \(0\.1 \* atr\)'
    
    scalp_call_buffer_replacement = """# Calculate dynamic buffer based on days to expiration
            buffer_factor = 0.1  # Default buffer factor
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 1:
                    buffer_factor = 0.05  # Half the buffer for 0-1 DTE
                elif days_to_expiration <= 2:
                    buffer_factor = 0.07  # 70% of normal buffer for 2 DTE
            
            stop_loss = breakout_low - (buffer_factor * atr)"""
    
    content = re.sub(scalp_call_buffer_pattern, scalp_call_buffer_replacement, content)
    
    # Now modify the PUT option buffer in the swing function
    # First find the section with the resistance level + buffer calculation
    swing_put_buffer_pattern = r'stop_loss = min\(resistance_level \+ \(0\.5 \* atr\), current_price \* 1\.05\)'
    
    swing_put_buffer_replacement = """# Calculate dynamic buffer based on days to expiration
                    max_percentage = 1.05  # Default 5% max buffer
                    buffer_factor = 0.5    # Default ATR factor
                    
                    # Adjust buffer based on days to expiration if available
                    if days_to_expiration is not None:
                        if days_to_expiration <= 1:
                            max_percentage = 1.01  # 1% for 0-1 DTE
                            buffer_factor = 0.2    # Smaller ATR multiple
                        elif days_to_expiration <= 2:
                            max_percentage = 1.02  # 2% for 2 DTE
                            buffer_factor = 0.3    # Smaller ATR multiple
                        elif days_to_expiration <= 5:
                            max_percentage = 1.03  # 3% for 3-5 DTE
                            buffer_factor = 0.4    # Smaller ATR multiple
                    
                    stop_loss = min(resistance_level + (buffer_factor * atr), current_price * max_percentage)"""
    
    content = re.sub(swing_put_buffer_pattern, swing_put_buffer_replacement, content)
    
    # Now modify the ATR-based stop loss for PUTs (when no resistance found)
    swing_put_atr_pattern = r'stop_loss = current_price \+ \(2 \* atr\)'
    
    swing_put_atr_replacement = """# Calculate dynamic buffer based on days to expiration
                    atr_multiple = 2.0  # Default 2x ATR
                    max_percentage = 1.05  # Default 5% cap
                    
                    # Adjust buffer based on days to expiration if available
                    if days_to_expiration is not None:
                        if days_to_expiration <= 1:
                            atr_multiple = 1.0  # 1x ATR for 0-1 DTE
                            max_percentage = 1.01  # 1% cap
                        elif days_to_expiration <= 2:
                            atr_multiple = 1.2  # 1.2x ATR for 2 DTE
                            max_percentage = 1.02  # 2% cap
                        elif days_to_expiration <= 5:
                            atr_multiple = 1.5  # 1.5x ATR for 3-5 DTE
                            max_percentage = 1.03  # 3% cap
                    
                    # Use the ATR multiple but cap at max_percentage
                    stop_loss = min(current_price + (atr_multiple * atr), current_price * max_percentage)"""
    
    content = re.sub(swing_put_atr_pattern, swing_put_atr_replacement, content)
    
    # Now modify the CALL option buffer in the swing function for consistency
    swing_call_buffer_pattern = r'stop_loss = max\(support_level - \(0\.5 \* atr\), current_price \* 0\.95\)'
    
    swing_call_buffer_replacement = """# Calculate dynamic buffer based on days to expiration
                    min_percentage = 0.95  # Default 5% max buffer
                    buffer_factor = 0.5    # Default ATR factor
                    
                    # Adjust buffer based on days to expiration if available
                    if days_to_expiration is not None:
                        if days_to_expiration <= 1:
                            min_percentage = 0.99  # 1% for 0-1 DTE
                            buffer_factor = 0.2    # Smaller ATR multiple
                        elif days_to_expiration <= 2:
                            min_percentage = 0.98  # 2% for 2 DTE
                            buffer_factor = 0.3    # Smaller ATR multiple
                        elif days_to_expiration <= 5:
                            min_percentage = 0.97  # 3% for 3-5 DTE
                            buffer_factor = 0.4    # Smaller ATR multiple
                    
                    stop_loss = max(support_level - (buffer_factor * atr), current_price * min_percentage)"""
    
    content = re.sub(swing_call_buffer_pattern, swing_call_buffer_replacement, content)
    
    # Now modify the ATR-based stop loss for CALLs (when no support found)
    swing_call_atr_pattern = r'stop_loss = current_price - \(2 \* atr\)'
    
    swing_call_atr_replacement = """# Calculate dynamic buffer based on days to expiration
                    atr_multiple = 2.0  # Default 2x ATR
                    min_percentage = 0.95  # Default 5% cap
                    
                    # Adjust buffer based on days to expiration if available
                    if days_to_expiration is not None:
                        if days_to_expiration <= 1:
                            atr_multiple = 1.0  # 1x ATR for 0-1 DTE
                            min_percentage = 0.99  # 1% cap
                        elif days_to_expiration <= 2:
                            atr_multiple = 1.2  # 1.2x ATR for 2 DTE
                            min_percentage = 0.98  # 2% cap
                        elif days_to_expiration <= 5:
                            atr_multiple = 1.5  # 1.5x ATR for 3-5 DTE
                            min_percentage = 0.97  # 3% cap
                    
                    # Use the ATR multiple but cap at min_percentage
                    stop_loss = max(current_price - (atr_multiple * atr), current_price * min_percentage)"""
    
    content = re.sub(swing_call_atr_pattern, swing_call_atr_replacement, content)
    
    # Also update the fallback percentages in case all other methods fail
    # For puts in swing trades
    fallback_put_pattern = r'stop_loss = current_price \* 1\.04  # 4% for swing'
    
    fallback_put_replacement = """# Adjust fallback based on days to expiration
                    max_percentage = 1.04  # Default 4% buffer
                    
                    # Adjust buffer based on days to expiration if available
                    if days_to_expiration is not None:
                        if days_to_expiration <= 1:
                            max_percentage = 1.01  # 1% for 0-1 DTE
                        elif days_to_expiration <= 2:
                            max_percentage = 1.02  # 2% for 2 DTE
                        elif days_to_expiration <= 5:
                            max_percentage = 1.03  # 3% for 3-5 DTE
                    
                    stop_loss = current_price * max_percentage  # Dynamic percentage for swing"""
    
    content = re.sub(fallback_put_pattern, fallback_put_replacement, content)
    
    # For puts in scalp trades
    fallback_scalp_put_pattern = r'stop_loss = current_price \* 1\.02  # 2% rise for ultra-short-term'
    
    fallback_scalp_put_replacement = """# Adjust fallback based on days to expiration
            max_percentage = 1.02  # Default 2% buffer for scalp
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 1:
                    max_percentage = 1.01  # 1% for 0-1 DTE
            
            stop_loss = current_price * max_percentage  # Dynamic percentage for scalp"""
    
    content = re.sub(fallback_scalp_put_pattern, fallback_scalp_put_replacement, content)
    
    # For calls in scalp trades
    fallback_scalp_call_pattern = r'stop_loss = current_price \* 0\.98  # 2% drop for ultra-short-term'
    
    fallback_scalp_call_replacement = """# Adjust fallback based on days to expiration
            min_percentage = 0.98  # Default 2% buffer for scalp
            
            # Adjust buffer based on days to expiration if available
            if days_to_expiration is not None:
                if days_to_expiration <= 1:
                    min_percentage = 0.99  # 1% for 0-1 DTE
            
            stop_loss = current_price * min_percentage  # Dynamic percentage for scalp"""
    
    content = re.sub(fallback_scalp_call_pattern, fallback_scalp_call_replacement, content)
    
    # Write the updated content back to technical_analysis.py
    with open('technical_analysis.py', 'w') as file:
        file.write(content)
    
    print("Dynamic stop loss buffer fix applied to technical_analysis.py")
    
if __name__ == "__main__":
    apply_dynamic_stop_loss_fix()