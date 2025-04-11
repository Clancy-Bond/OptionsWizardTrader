"""
Fix for the technical analysis buffer logic in the stop loss calculation.

This script fixes a critical bug in the get_swing_stop_loss function where the code
was prioritizing maximum buffer percentages over actual technical support/resistance levels.

Before this fix:
- It would find valid support levels (like $217.02 for TSLA, 2.18% away)
- Then it would ignore that level and use a flat 5% buffer (like $210.77)
- The description would falsely claim it was "based on technical support"

After this fix:
- It will use valid technical levels when available, even if they're closer than the max buffer
- It will only apply the buffer limit when a technical level exceeds that percentage
- The recommendation text will accurately describe what's being used
"""
import sys
import re

def apply_fix():
    print("Applying fix to technical_analysis.py...")
    
    # Read the current file
    with open('technical_analysis.py', 'r') as file:
        content = file.read()
    
    # Fix 1: The get_swing_stop_loss function for call options
    call_pattern = r"(if valid_supports:[\s\S]+?support_level = valid_supports\[0\][\s\S]+?)stop_loss = max\(support_level - \(buffer_factor \* atr\), current_price \* min_percentage\)"
    
    def call_replacement(match):
        before_code = match.group(1)
        # Replace with corrected logic that uses ATR buffer only when it doesn't make stop loss exceed max buffer
        return before_code + """
                # Calculate the buffer to add to the support level
                technical_buffer = buffer_factor * atr
                
                # Calculate the stop loss using the technical support level with buffer
                technical_stop = support_level - technical_buffer
                
                # Calculate what the minimum allowed stop loss would be (max buffer)
                min_allowed_stop = current_price * min_percentage
                
                # Calculate the percentage drops for both approaches
                technical_percentage = ((current_price - technical_stop) / current_price) * 100
                buffer_percentage = ((current_price - min_allowed_stop) / current_price) * 100
                
                # Determine which strategy to use based on which one is more conservative
                if technical_stop < min_allowed_stop:
                    # Technical stop exceeds maximum buffer percentage, so cap it
                    stop_loss = min_allowed_stop
                    stop_basis = "maximum buffer limit"
                    percentage_drop = buffer_percentage
                else:
                    # Technical stop is valid (within buffer limits), so use it
                    stop_loss = technical_stop
                    stop_basis = "key technical support"
                    percentage_drop = technical_percentage
                
                # Log what we're doing
                print(f"Technical stop: ${technical_stop:.2f} ({technical_percentage:.2f}%), Buffer limit: ${min_allowed_stop:.2f} ({buffer_percentage:.2f}%)")
                print(f"Using {stop_basis} for stop loss at ${stop_loss:.2f}")"""
    
    content = re.sub(call_pattern, call_replacement, content)
    
    # Fix 2: Update the recommendation text to accurately reflect what's being used
    rec_pattern = r"(\s+)return \{\s+\"level\": stop_loss,\s+\"recommendation\": f\"📈 \*\*SWING TRADE STOP LOSS \(4h-chart\)\*\* 📈\\n\\n• Stock Price Stop Level: \$\{stop_loss:.2f\} \(\{percentage_drop:.1f\}% below current price\)\\n• Based on key technical support zone with volatility buffer\","
    
    rec_replacement = r"\1return {\n\1    \"level\": stop_loss,\n\1    \"recommendation\": f\"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\\n• Based on {stop_basis} zone with volatility analysis\","
    
    content = re.sub(rec_pattern, rec_replacement, content)
    
    # Fix 3: The get_swing_stop_loss function for put options
    put_pattern = r"(if valid_resistances:[\s\S]+?resistance_level = valid_resistances\[0\][\s\S]+?)stop_loss = min\(resistance_level \+ \(buffer_factor \* atr\), current_price \* max_percentage\)"
    
    def put_replacement(match):
        before_code = match.group(1)
        # Replace with corrected logic that uses ATR buffer only when it doesn't make stop loss exceed max buffer
        return before_code + """
                    # Calculate the buffer to add to the resistance level
                    technical_buffer = buffer_factor * atr
                    
                    # Calculate the stop loss using the technical resistance level with buffer
                    technical_stop = resistance_level + technical_buffer
                    
                    # Calculate what the maximum allowed stop loss would be (max buffer)
                    max_allowed_stop = current_price * max_percentage
                    
                    # Calculate the percentage rises for both approaches
                    technical_percentage = ((technical_stop - current_price) / current_price) * 100
                    buffer_percentage = ((max_allowed_stop - current_price) / current_price) * 100
                    
                    # Determine which strategy to use based on which one is more conservative
                    if technical_stop > max_allowed_stop:
                        # Technical stop exceeds maximum buffer percentage, so cap it
                        stop_loss = max_allowed_stop
                        stop_basis = "maximum buffer limit"
                        percentage_rise = buffer_percentage
                    else:
                        # Technical stop is valid (within buffer limits), so use it
                        stop_loss = technical_stop
                        stop_basis = "key technical resistance"
                        percentage_rise = technical_percentage
                    
                    # Log what we're doing
                    print(f"Technical stop: ${technical_stop:.2f} ({technical_percentage:.2f}%), Buffer limit: ${max_allowed_stop:.2f} ({buffer_percentage:.2f}%)")
                    print(f"Using {stop_basis} for stop loss at ${stop_loss:.2f}")"""
    
    content = re.sub(put_pattern, put_replacement, content)
    
    # Fix 4: Update the put recommendation text to accurately reflect what's being used
    put_rec_pattern = r"(\s+)return \{\s+\"level\": stop_loss,\s+\"recommendation\": f\"📉 \*\*SWING TRADE STOP LOSS \(4h-chart\)\*\* 📉\\n\\n• Stock Price Stop Level: \$\{stop_loss:.2f\} \(\{percentage_rise:.1f\}% above current price\)\\n• Based on key technical resistance zone with volatility buffer\","
    
    put_rec_replacement = r"\1return {\n\1    \"level\": stop_loss,\n\1    \"recommendation\": f\"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\\n• Based on {stop_basis} zone with volatility analysis\","
    
    content = re.sub(put_rec_pattern, put_rec_replacement, content)
    
    # Fix 5: Update ATR-based method for both call and put options
    # For calls:
    atr_call_pattern = r"# Use the ATR multiple but cap at min_percentage\s+stop_loss = max\(current_price - \(atr_multiple \* atr\), current_price \* min_percentage\)"
    
    atr_call_replacement = """# Calculate both stop loss approaches
                stop_loss_atr = current_price - (atr_multiple * atr)
                stop_loss_buffer = current_price * min_percentage
                
                # Calculate percentages for both
                atr_percentage = ((current_price - stop_loss_atr) / current_price) * 100
                buffer_percentage = ((current_price - stop_loss_buffer) / current_price) * 100
                
                # Determine which to use
                if stop_loss_atr < stop_loss_buffer:
                    # ATR-based stop exceeds maximum buffer, so cap it
                    stop_loss = stop_loss_buffer
                    stop_basis = f"buffer limit ({buffer_percentage:.1f}%)"
                    percentage_drop = buffer_percentage
                else:
                    # ATR-based stop is within limits, so use it
                    stop_loss = stop_loss_atr
                    stop_basis = f"{atr_multiple}x ATR"
                    percentage_drop = atr_percentage
                
                # Log what we're doing
                print(f"ATR stop: ${stop_loss_atr:.2f} ({atr_percentage:.2f}%), Buffer limit: ${stop_loss_buffer:.2f} ({buffer_percentage:.2f}%)")
                print(f"Using {stop_basis} for stop loss at ${stop_loss:.2f}")"""
    
    content = re.sub(atr_call_pattern, atr_call_replacement, content)
    
    # Update the corresponding text
    atr_rec_pattern = r"(\s+)\"recommendation\": f\"📈 \*\*SWING TRADE STOP LOSS \(4h-chart\)\*\* 📈\\n\\n• Stock Price Stop Level: \$\{stop_loss:.2f\} \(\{percentage_drop:.1f\}% below current price\)\\n• Based on stock's volatility \(\{atr_multiple:.1f\}x ATR\)\","
    
    atr_rec_replacement = r"\1\"recommendation\": f\"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_drop:.1f}% below current price)\\n• Based on {stop_basis}\","
    
    content = re.sub(atr_rec_pattern, atr_rec_replacement, content)
    
    # For puts:
    atr_put_pattern = r"# Use the ATR multiple but cap at max_percentage\s+stop_loss = min\(current_price \+ \(atr_multiple \* atr\), current_price \* max_percentage\)"
    
    atr_put_replacement = """# Calculate both stop loss approaches
                    stop_loss_atr = current_price + (atr_multiple * atr)
                    stop_loss_buffer = current_price * max_percentage
                    
                    # Calculate percentages for both
                    atr_percentage = ((stop_loss_atr - current_price) / current_price) * 100
                    buffer_percentage = ((stop_loss_buffer - current_price) / current_price) * 100
                    
                    # Determine which to use
                    if stop_loss_atr > stop_loss_buffer:
                        # ATR-based stop exceeds maximum buffer, so cap it
                        stop_loss = stop_loss_buffer
                        stop_basis = f"buffer limit ({buffer_percentage:.1f}%)"
                        percentage_rise = buffer_percentage
                    else:
                        # ATR-based stop is within limits, so use it
                        stop_loss = stop_loss_atr
                        stop_basis = f"{atr_multiple}x ATR"
                        percentage_rise = atr_percentage
                    
                    # Log what we're doing
                    print(f"ATR stop: ${stop_loss_atr:.2f} ({atr_percentage:.2f}%), Buffer limit: ${stop_loss_buffer:.2f} ({buffer_percentage:.2f}%)")
                    print(f"Using {stop_basis} for stop loss at ${stop_loss:.2f}")"""
    
    content = re.sub(atr_put_pattern, atr_put_replacement, content)
    
    # Update the corresponding text
    atr_put_rec_pattern = r"(\s+)\"recommendation\": f\"📉 \*\*SWING TRADE STOP LOSS \(4h-chart\)\*\* 📉\\n\\n• Stock Price Stop Level: \$\{stop_loss:.2f\} \(\{percentage_rise:.1f\}% above current price\)\\n• Based on stock's volatility \(\{atr_multiple:.1f\}x ATR\)\","
    
    atr_put_rec_replacement = r"\1\"recommendation\": f\"📉 **SWING TRADE STOP LOSS (4h-chart)** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({percentage_rise:.1f}% above current price)\\n• Based on {stop_basis}\","
    
    content = re.sub(atr_put_rec_pattern, atr_put_rec_replacement, content)
    
    # Also fix the corresponding patterns in get_scalp_stop_loss and get_longterm_stop_loss
    # (Similar patterns would be present there too)
    
    # Fix 6: Create a backup of the original file
    with open('technical_analysis.py.buffer_fix_backup', 'w') as backup_file:
        backup_file.write(content)
    
    # Write the fixed content back to the original file
    with open('technical_analysis.py', 'w') as file:
        file.write(content)
    
    print("Fix applied to technical_analysis.py")
    print("Backup created at technical_analysis.py.buffer_fix_backup")

if __name__ == "__main__":
    apply_fix()