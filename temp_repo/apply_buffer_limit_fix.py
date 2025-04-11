#!/usr/bin/env python3
"""
Apply a fix to discord_bot.py to enforce buffer limits based on DTE.
This ensures the bot falls back to DTE-based buffer percentages when technical analysis
recommends stop loss levels that exceed these limitations.
"""

import os
import shutil
import sys

def apply_fix():
    """Apply the fix to discord_bot.py"""
    # Load the combined_scalp_stop_loss.py file
    try:
        with open('combined_scalp_stop_loss.py', 'r') as f:
            content = f.read()
        
        # Create a backup
        with open('combined_scalp_stop_loss.py.bak', 'w') as f:
            f.write(content)
            
        # Find and fix the get_combined_scalp_stop_loss function
        old_code = """        # Calculate both stop loss methods
        wick_stop = get_wick_based_stop(hist_data, option_type, atr, lookback_candles=3)
        vwap_stop, requires_candle_close, vwap_is_valid = get_vwap_based_stop(hist_data, option_type, current_price)
        
        # If VWAP is not a valid stop (wrong side of price), always use wick-based stop
        if not vwap_is_valid:
            stop_loss = wick_stop
            stop_method = "wick-based"
            requires_close = False
            print(f"VWAP at {vwap_stop:.2f} is not valid as stop for {option_type} option with current price {current_price:.2f}, using wick-based stop at {wick_stop:.2f}")
        else:
            # Calculate distance from current price for each method
            wick_distance = calculate_stop_distance(current_price, wick_stop, option_type)
            vwap_distance = calculate_stop_distance(current_price, vwap_stop, option_type)
            
            # Choose the tighter stop (closer to current price)
            if wick_distance <= vwap_distance:
                stop_loss = wick_stop
                stop_method = "wick-based"
                requires_close = False
            else:
                stop_loss = vwap_stop
                stop_method = "VWAP-based"
                requires_close = requires_candle_close"""
                    
        new_code = """        # Calculate both stop loss methods
        wick_stop = get_wick_based_stop(hist_data, option_type, atr, lookback_candles=3)
        vwap_stop, requires_candle_close, vwap_is_valid = get_vwap_based_stop(hist_data, option_type, current_price)
        
        # Calculate DTE-based maximum buffer percentage for CALL options
        max_buffer_pct = 0.05  # Default 5% maximum
        if days_to_expiration is not None and option_type.lower() == 'call':
            if days_to_expiration <= 1:
                max_buffer_pct = 0.01  # 1% for 0-1 DTE
            elif days_to_expiration <= 2:
                max_buffer_pct = 0.02  # 2% for 2 DTE
            elif days_to_expiration <= 5:
                max_buffer_pct = 0.03  # 3% for 3-5 DTE
            
        # Calculate max allowed stop level for CALL options based on buffer percentage
        min_allowed_stop = current_price * (1 - max_buffer_pct) if option_type.lower() == 'call' else 0
        
        # If VWAP is not a valid stop (wrong side of price), always use wick-based stop
        if not vwap_is_valid:
            stop_loss = wick_stop
            stop_method = "wick-based"
            requires_close = False
            print(f"VWAP at {vwap_stop:.2f} is not valid as stop for {option_type} option with current price {current_price:.2f}, using wick-based stop at {wick_stop:.2f}")
        else:
            # Calculate distance from current price for each method
            wick_distance = calculate_stop_distance(current_price, wick_stop, option_type)
            vwap_distance = calculate_stop_distance(current_price, vwap_stop, option_type)
            
            # Choose the tighter stop (closer to current price)
            if wick_distance <= vwap_distance:
                stop_loss = wick_stop
                stop_method = "wick-based"
                requires_close = False
            else:
                stop_loss = vwap_stop
                stop_method = "VWAP-based"
                requires_close = requires_candle_close
        
        # For CALL options, ensure we don't exceed the maximum buffer
        if option_type.lower() == 'call' and stop_loss < min_allowed_stop:
            # Technical stop exceeds maximum buffer, so cap it
            stop_loss = min_allowed_stop
            stop_method = f"{stop_method} (capped at {max_buffer_pct*100:.1f}% max)"
            print(f"Stop loss for {option_type} option capped at ${stop_loss:.2f} ({max_buffer_pct*100:.1f}% max buffer)")"""
        
        # Replace the block
        new_content = content.replace(old_code, new_code)
        
        # Save the changed file
        with open('combined_scalp_stop_loss.py', 'w') as f:
            f.write(new_content)
            
        print("✓ Successfully applied buffer limit fix to combined_scalp_stop_loss.py")
        print("  A backup was created in combined_scalp_stop_loss.py.bak")
        return True
    
    except Exception as e:
        print(f"✗ Failed to apply fix: {str(e)}")
        return False

if __name__ == "__main__":
    print("Applying buffer limit fix...")
    apply_fix()
    
    print("\nTo test the fix, run: python verify_buffer_limits.py")
    print("Note: The Discord bot should be restarted for changes to take effect.")