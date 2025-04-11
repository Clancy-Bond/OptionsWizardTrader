#!/usr/bin/env python3
"""
Careful fix for the buffer logic in the stop loss calculation.
This fix is manually applied to ensure there are no syntax errors.
"""

import os
import sys

def apply_fix():
    """
    Carefully apply the buffer limit fixes for technical_analysis.py
    to ensure 3-5 DTE limits are properly enforced.
    """
    # Load the file
    file_path = 'technical_analysis.py'
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Create a backup
        with open(file_path + '.buffer_fix.bak', 'w') as backup:
            backup.writelines(lines)
            
        # Locate the get_scalp_stop_loss definition line
        scalp_fn_index = None
        for i, line in enumerate(lines):
            if line.strip().startswith('def get_scalp_stop_loss'):
                scalp_fn_index = i
                break
        
        if scalp_fn_index is None:
            print("Could not find get_scalp_stop_loss function. Aborting.")
            return False
        
        # Insert buffer percentage determination code
        buffer_code = [
            '    # Determine DTE-based buffer percentages\n',
            '    max_buffer_pct = 0.05  # Default 5% buffer\n',
            '    if days_to_expiration is not None:\n',
            '        if days_to_expiration <= 1:\n',
            '            max_buffer_pct = 0.01  # 1% for 0-1 DTE\n',
            '        elif days_to_expiration <= 2:\n',
            '            max_buffer_pct = 0.02  # 2% for 2 DTE\n',
            '        elif days_to_expiration <= 5:\n',
            '            max_buffer_pct = 0.03  # 3% for 3-5 DTE\n',
            '    \n',
            '    # For PUT options with 60+ DTE, use 7% buffer\n',
            '    if option_type.lower() == "put" and days_to_expiration is not None and days_to_expiration > 60:\n',
            '        max_buffer_pct = 0.07\n',
            '    \n'
        ]
        
        # Insert after function definition and docstring
        # Find docstring end
        docstring_end = scalp_fn_index + 1
        while docstring_end < len(lines) and ('"""' not in lines[docstring_end] and "'''" not in lines[docstring_end]):
            docstring_end += 1
        
        # Skip to the line after docstring ends
        if '"""' in lines[docstring_end] or "'''" in lines[docstring_end]:
            docstring_end += 1
            
        # Insert buffer code
        for i, line in enumerate(buffer_code):
            lines.insert(docstring_end + i, line)
            
        # Add buffer variables in the try block
        try_block_start = None
        for i in range(docstring_end, len(lines)):
            if lines[i].strip() == 'try:':
                try_block_start = i
                break
        
        if try_block_start is None:
            print("Could not find try block. Aborting.")
            return False
            
        # Find where to add buffer limit variables
        buffer_vars_index = try_block_start + 1
        while buffer_vars_index < len(lines) and 'atr =' not in lines[buffer_vars_index]:
            buffer_vars_index += 1
        
        # Insert after ATR calculation
        if buffer_vars_index < len(lines):
            buffer_vars_index += 1
            buffer_vars_code = [
                '        # Calculate buffer limit values\n',
                '        if option_type.lower() == "call":\n',
                '            min_allowed_stop = current_price * (1 - max_buffer_pct)  # Minimum allowed stop level\n',
                '        else:  # PUT option\n',
                '            max_allowed_stop = current_price * (1 + max_buffer_pct)  # Maximum allowed stop level\n',
                '\n'
            ]
            
            for i, line in enumerate(buffer_vars_code):
                lines.insert(buffer_vars_index + i, line)
                
        # Now add the enforcement for CALL options
        call_stop_index = None
        for i in range(buffer_vars_index, len(lines)):
            if "stop_loss = max(recent_low - atr_buffer, current_price * buffer_percentage)" in lines[i]:
                call_stop_index = i
                break
        
        if call_stop_index is not None:
            call_stop_index += 1
            buffer_check_code = [
                '            # Ensure we don\'t exceed the maximum buffer for CALL options\n',
                '            if stop_loss < min_allowed_stop:\n',
                '                stop_loss = min_allowed_stop\n',
                '                print(f"CALL option stop capped at max buffer of {max_buffer_pct*100:.1f}%: ${stop_loss:.2f}")\n',
                '\n'
            ]
            
            for i, line in enumerate(buffer_check_code):
                lines.insert(call_stop_index + i, line)
                
        # Now add the enforcement for PUT options
        put_stop_index = None
        for i in range(buffer_vars_index, len(lines)):
            if "stop_loss = min(recent_high + atr_buffer, current_price * buffer_percentage)" in lines[i]:
                put_stop_index = i
                break
        
        if put_stop_index is not None:
            put_stop_index += 1
            buffer_check_code = [
                '            # Ensure we don\'t exceed the maximum buffer for PUT options\n',
                '            if stop_loss > max_allowed_stop:\n',
                '                stop_loss = max_allowed_stop\n',
                '                print(f"PUT option stop capped at max buffer of {max_buffer_pct*100:.1f}%: ${stop_loss:.2f}")\n',
                '\n'
            ]
            
            for i, line in enumerate(buffer_check_code):
                lines.insert(put_stop_index + i, line)
        
        # Save changes
        with open(file_path, 'w') as file:
            file.writelines(lines)
            
        print(f"✓ Successfully applied buffer limit fix to {file_path}")
        print(f"  A backup was created at {file_path}.buffer_fix.bak")
        return True
        
    except Exception as e:
        print(f"✗ Error applying fix: {str(e)}")
        return False

if __name__ == "__main__":
    print("Applying careful buffer limit fix...")
    apply_fix()
    print("\nPlease restart the Discord bot for the changes to take effect.")