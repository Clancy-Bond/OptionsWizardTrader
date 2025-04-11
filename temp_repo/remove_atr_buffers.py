#!/usr/bin/env python3
"""
Script to remove ATR buffers from the stop loss calculation system.
This will make stop losses based only on exact technical levels (support/resistance)
with the percentage-based maximum limits still applying.
"""
import re
import os
import shutil

def backup_file(filepath):
    """Create a backup of the file being modified."""
    backup_path = f"{filepath}.bak"
    try:
        shutil.copy2(filepath, backup_path)
        print(f"✓ Created backup: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create backup of {filepath}: {str(e)}")
        return False

def modify_scale_atr_function():
    """Modify the scale_atr_for_dte function to effectively remove ATR buffers."""
    filepath = "technical_analysis.py"
    
    if not backup_file(filepath):
        return False
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Modify the scale_atr_for_dte function to return near-zero values
        # This effectively removes ATR buffers while keeping the function interface intact
        pattern = r"def scale_atr_for_dte\(atr, days_to_expiration, pattern_type=\"breakout\", trade_type=None\):(.*?)return atr \* base_multiplier \* dte_multiplier"
        replacement = r"def scale_atr_for_dte(atr, days_to_expiration, pattern_type=\"breakout\", trade_type=None):\n    # ATR buffers removed - returning near-zero value\n    return 0.0001  # Effectively removes buffer while avoiding division by zero issues"
        
        modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Write modified content back to file
        with open(filepath, 'w') as file:
            file.write(modified_content)
        
        print(f"✓ Modified scale_atr_for_dte function in {filepath}")
        return True
    except Exception as e:
        print(f"✗ Failed to modify {filepath}: {str(e)}")
        return False

def modify_swing_stop_loss():
    """Modify get_swing_stop_loss to remove ATR buffer calculations."""
    filepath = "technical_analysis.py"
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Patterns to find and modify ATR buffer calculations in swing stop loss function
        patterns = [
            # For CALL options (support levels)
            (r"technical_buffer = buffer_factor \* atr", r"technical_buffer = 0  # ATR buffer removed"),
            
            # For PUT options (resistance levels)
            (r"technical_buffer = buffer_factor \* atr", r"technical_buffer = 0  # ATR buffer removed"),
            
            # For ATR-based stops when no support/resistance found (calls)
            (r"stop_loss_atr = current_price - \(atr_multiple \* atr\)", 
             r"stop_loss_atr = current_price - (0.0001)  # ATR buffer removed, using price-based only"),
            
            # For ATR-based stops when no support/resistance found (puts)
            (r"stop_loss_atr = current_price \+ \(atr_multiple \* atr\)", 
             r"stop_loss_atr = current_price + (0.0001)  # ATR buffer removed, using price-based only")
        ]
        
        modified_content = content
        for pattern, replacement in patterns:
            modified_content = re.sub(pattern, replacement, modified_content)
        
        # Write modified content back to file
        with open(filepath, 'w') as file:
            file.write(modified_content)
        
        print(f"✓ Modified ATR buffer calculations in get_swing_stop_loss")
        return True
    except Exception as e:
        print(f"✗ Failed to modify get_swing_stop_loss: {str(e)}")
        return False

def modify_enhanced_atr_stop_loss():
    """Modify the enhanced_atr_stop_loss.py file to remove ATR buffers."""
    filepath = "enhanced_atr_stop_loss.py"
    
    if not backup_file(filepath):
        return False
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Pattern to find and modify ATR calculation in calculate_breakout_stop_loss
        pattern1 = r"atr_buffer = scale_atr_for_dte\(atr, days_to_expiration or 14, \"breakout\", trade_type\)"
        replacement1 = r"atr_buffer = 0.0001  # ATR buffer removed"
        
        # Pattern to find and modify ATR calculation in calculate_engulfing_stop_loss
        pattern2 = r"atr_buffer = scale_atr_for_dte\(atr, days_to_expiration or 14, \"engulfing\", trade_type\)"
        replacement2 = r"atr_buffer = 0.0001  # ATR buffer removed"
        
        # Apply replacements
        modified_content = content.replace(pattern1, replacement1).replace(pattern2, replacement2)
        
        # Write modified content back to file
        with open(filepath, 'w') as file:
            file.write(modified_content)
        
        print(f"✓ Modified ATR buffer calculations in {filepath}")
        return True
    except Exception as e:
        print(f"✗ Failed to modify {filepath}: {str(e)}")
        return False

def modify_combined_scalp_stop_loss():
    """Modify the combined_scalp_stop_loss.py file to remove ATR buffers."""
    filepath = "combined_scalp_stop_loss.py"
    
    if not backup_file(filepath):
        return False
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Find and modify ATR buffer calculations in get_wick_based_stop
        pattern = r"if atr:\s+buffer = atr \* 0.5"
        replacement = r"if atr:\n        buffer = 0  # ATR buffer removed"
        
        modified_content = re.sub(pattern, replacement, content)
        
        # Write modified content back to file
        with open(filepath, 'w') as file:
            file.write(modified_content)
        
        print(f"✓ Modified ATR buffer calculations in {filepath}")
        return True
    except Exception as e:
        print(f"✗ Failed to modify {filepath}: {str(e)}")
        return False

def main():
    """Main function to coordinate all modifications."""
    print("Starting ATR buffer removal process...")
    
    # Perform modifications
    success = True
    success &= modify_scale_atr_function()
    success &= modify_swing_stop_loss()
    success &= modify_enhanced_atr_stop_loss()
    success &= modify_combined_scalp_stop_loss()
    
    if success:
        print("\n✅ ATR buffer removal completed successfully!")
        print("Stop losses will now be set at exact technical levels (support/resistance)")
        print("with percentage-based maximum limits still applying.")
        print("\nTo revert changes, run: python restore_from_backup.py")
    else:
        print("\n❌ ATR buffer removal encountered issues.")
        print("Some files may not have been modified correctly.")
        print("Check the logs above for details.")
    
    return success

if __name__ == "__main__":
    main()