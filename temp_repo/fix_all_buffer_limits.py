#!/usr/bin/env python3
"""
Apply comprehensive buffer limit fix to ensure all timeframes respect the appropriate
maximum buffer limits based on DTE values:

CALL Options:
- 1.0% for 0-1 DTE
- 2.0% for 2 DTE
- 3.0% for 3-5 DTE
- 5.0% for 6-60 DTE
- 5.0% for 60+ DTE

PUT Options:
- 1.0% for 0-1 DTE
- 2.0% for 2 DTE  
- 3.0% for 3-5 DTE
- 5.0% for 6-60 DTE
- 7.0% for 60+ DTE
"""

import os
import shutil
import sys

def fix_technical_analysis():
    """Apply buffer fix to technical_analysis.py"""
    try:
        # Load the technical_analysis.py file
        with open('technical_analysis.py', 'r') as f:
            content = f.read()
        
        # Create a backup
        with open('technical_analysis.py.buffer_fix.bak', 'w') as f:
            f.write(content)
        
        # Fix get_scalp_stop_loss function
        old_code = "def get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):"
        new_code = """def get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
    # Determine appropriate buffer based on DTE
    max_buffer_pct = 0.05  # Default is 5%
    if days_to_expiration is not None:
        if days_to_expiration <= 1:
            max_buffer_pct = 0.01  # 1% for 0-1 DTE
        elif days_to_expiration <= 2:
            max_buffer_pct = 0.02  # 2% for 2 DTE
        elif days_to_expiration <= 5:
            max_buffer_pct = 0.03  # 3% for 3-5 DTE
            
    # For PUT options at 60+ DTE, allow up to 7%
    if option_type.lower() == 'put' and days_to_expiration is not None and days_to_expiration > 60:
        max_buffer_pct = 0.07"""
        new_content = content.replace(old_code, new_code)
        
        # Fix the calculation for 3-5 DTE in get_scalp_stop_loss
        old_code_2 = """    try:
        # For scalp trading, we'll look at small timeframes
        # Get 5-minute data for short-term/day trading
        hist_data = stock.history(period="5d", interval="5m")
        
        # Fall back to hourly if 5m data is limited
        if hist_data.empty or len(hist_data) < 10:
            hist_data = stock.history(period="5d", interval="1h")
            timeframe = "1h"
        else:
            timeframe = "5m"
        
        # Calculate ATR for volatility-based stop
        atr = calculate_atr(hist_data, window=14, trade_type=trade_type)  # Standard 14-period ATR
        
        if option_type.lower() == 'call':
            # For call options (long bias)"""
            
        new_code_2 = """    try:
        # For scalp trading, we'll look at small timeframes
        # Get 5-minute data for short-term/day trading
        hist_data = stock.history(period="5d", interval="5m")
        
        # Fall back to hourly if 5m data is limited
        if hist_data.empty or len(hist_data) < 10:
            hist_data = stock.history(period="5d", interval="1h")
            timeframe = "1h"
        else:
            timeframe = "5m"
        
        # Calculate ATR for volatility-based stop
        atr = calculate_atr(hist_data, window=14, trade_type=trade_type)  # Standard 14-period ATR
        
        # Calculate buffer limit values for both CALL and PUT options
        if option_type.lower() == 'call':
            # Maximum allowed drop based on max_buffer_pct
            min_allowed_stop = current_price * (1 - max_buffer_pct)
        else:
            # Maximum allowed rise based on max_buffer_pct
            max_allowed_stop = current_price * (1 + max_buffer_pct)
        
        if option_type.lower() == 'call':
            # For call options (long bias)"""
        
        new_content = new_content.replace(old_code_2, new_code_2)
        
        # Ensure we enforce the buffer limit for get_scalp_stop_loss for CALL options
        old_code_3 = """            # Use the higher of the two (more conservative)
            stop_loss = max(recent_low - atr_buffer, current_price * buffer_percentage)
            
            # Calculate percentage drop
            percentage_drop = ((current_price - stop_loss) / current_price) * 100"""
        
        new_code_3 = """            # Use the higher of the two (more conservative)
            stop_loss = max(recent_low - atr_buffer, current_price * buffer_percentage)
            
            # Ensure we don't exceed the maximum buffer
            if stop_loss < min_allowed_stop:
                stop_loss = min_allowed_stop
                print(f"CALL option stop capped at max buffer of {max_buffer_pct*100:.1f}%: ${stop_loss:.2f}")
                
            # Calculate percentage drop
            percentage_drop = ((current_price - stop_loss) / current_price) * 100"""
            
        new_content = new_content.replace(old_code_3, new_code_3)
        
        # Ensure we enforce the buffer limit for get_scalp_stop_loss for PUT options
        old_code_4 = """            # Use the lower of the two (more conservative)
            stop_loss = min(recent_high + atr_buffer, current_price * buffer_percentage)
            
            # Calculate percentage rise
            percentage_rise = ((stop_loss - current_price) / current_price) * 100"""
        
        new_code_4 = """            # Use the lower of the two (more conservative)
            stop_loss = min(recent_high + atr_buffer, current_price * buffer_percentage)
            
            # Ensure we don't exceed the maximum buffer
            if stop_loss > max_allowed_stop:
                stop_loss = max_allowed_stop
                print(f"PUT option stop capped at max buffer of {max_buffer_pct*100:.1f}%: ${stop_loss:.2f}")
                
            # Calculate percentage rise
            percentage_rise = ((stop_loss - current_price) / current_price) * 100"""
            
        new_content = new_content.replace(old_code_4, new_code_4)
        
        # Save the changes
        with open('technical_analysis.py', 'w') as f:
            f.write(new_content)
            
        print("✓ Successfully fixed buffer limits in technical_analysis.py")
        return True
    
    except Exception as e:
        print(f"✗ Failed to fix technical_analysis.py: {str(e)}")
        return False

if __name__ == "__main__":
    print("Applying comprehensive buffer limit fixes...")
    fix_technical_analysis()
    
    print("\nTo test the fixes, run: python verify_buffer_limits.py")
    print("Note: The Discord bot should be restarted for changes to take effect.")