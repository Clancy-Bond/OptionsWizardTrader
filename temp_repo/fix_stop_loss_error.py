"""
Fix the primary key error in get_stop_loss_recommendation function
using a simpler, more direct approach.
"""

def apply_fix():
    """
    Apply a targeted fix to ensure the primary key is always set
    and the trade_horizon is always in the result dictionary.
    """
    with open('technical_analysis.py', 'r') as file:
        content = file.read()
    
    # Find the end of get_stop_loss_recommendation function before the final return result
    # Add code to ensure all keys exist
    target_before = "        return result"
    replacement = """        # Ensure all necessary keys exist to prevent KeyError
        if 'primary' not in result:
            # Default to swing recommendation as primary if not already set
            result['primary'] = result['swing']
            
        # Always ensure trade_horizon is in the result
        result['trade_horizon'] = trade_horizon
        
        return result"""
    
    # Apply the fix
    content = content.replace(target_before, replacement)
    
    # Apply the same fix to the filtered_result
    target_before = "            return filtered_result"
    replacement = """            # Ensure all necessary keys exist in filtered_result
            if 'primary' not in filtered_result:
                filtered_result['primary'] = filtered_result.get('swing', result.get('swing'))
                
            # Always ensure trade_horizon is in the filtered_result
            filtered_result['trade_horizon'] = trade_horizon
            
            return filtered_result"""
    
    # Apply the fix
    content = content.replace(target_before, replacement)
    
    # Add enhanced exception handling to all formatting sections
    # First, wrap the scalp formatting in try-except
    target_scalp_start = "            if trade_horizon == \"scalp\":"
    target_scalp_end = "                    )"
    try_block_start = "            if trade_horizon == \"scalp\":\n                try:"
    try_block_end = "                    )\n                except Exception as e:\n                    print(f\"Error formatting scalp recommendation: {e}\")"
    
    # Find the positions
    scalp_start_pos = content.find(target_scalp_start)
    scalp_end_pos = content.find(target_scalp_end, scalp_start_pos) + len(target_scalp_end)
    
    if scalp_start_pos >= 0 and scalp_end_pos >= 0:
        # Extract the block
        scalp_block = content[scalp_start_pos:scalp_end_pos]
        # Indent the whole block one more level
        indented_block = '\n'.join(['    ' + line for line in scalp_block.split('\n')])
        # Replace with try-except
        content = content[:scalp_start_pos] + try_block_start + indented_block[len(target_scalp_start):] + try_block_end + content[scalp_end_pos:]
    
    # Write the changes
    with open('technical_analysis.py', 'w') as file:
        file.write(content)
    
    print("Successfully applied targeted fixes to technical_analysis.py")
    
    # Fix the buffer adjustment code to better handle very small adjustments
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Update the buffer checking code to avoid logging when the adjustment is negligible
    target = """            print(f"Adjusting stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE")"""
    replacement = """            # Calculate how much we're adjusting (absolute percentage of current price)
            adjustment_percentage = abs(adjusted_stop_loss - stop_loss) / current_price * 100
            
            # Only log if adjustment is significant (greater than 0.01%)
            if adjustment_percentage > 0.01:
                print(f"Adjusting stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE")
                print(f"Current price: ${current_price:.2f}, adjustment amount: {adjustment_percentage:.2f}% of price")"""
    
    content = content.replace(target, replacement)
    
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Successfully updated buffer enforcement in discord_bot.py")

if __name__ == "__main__":
    apply_fix()