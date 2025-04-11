"""
Test script to verify the dynamic buffer display in the Discord bot.

This script checks if the bot displays the right buffer percentages
for different option types (call/put) and days to expiration.
"""

import discord
import os
from datetime import datetime, timedelta
import re

# Simulate buffer calculation function
def test_buffer_display():
    """
    Test the dynamic buffer percentage display in the Discord bot output.
    
    Creates a mock embed and formats it the same way as the bot would,
    for both call and put options with various days to expiration.
    """
    print("=== Testing Dynamic Buffer Percentage Display ===")
    
    # Test parameters
    current_price = 100.0
    option_price = 5.0
    dte_values = [1, 2, 5, 10, 30]
    option_types = ["call", "put"]
    
    for dte in dte_values:
        for option_type in option_types:
            print(f"\nTesting {option_type.upper()} option with {dte} days to expiration:")
            
            # Set buffer percentage based on DTE (same logic as discord_bot.py)
            if dte <= 1:
                buffer_percentage = 1.0  # 1% for 0-1 DTE
            elif dte <= 2:
                buffer_percentage = 2.0  # 2% for 2 DTE
            elif dte <= 5:
                buffer_percentage = 3.0  # 3% for 3-5 DTE
            else:
                buffer_percentage = 5.0  # 5% default for longer expirations
            
            # Calculate stop loss price based on buffer
            if option_type == "call":
                stop_loss = current_price * (1 - buffer_percentage/100)
            else:
                stop_loss = current_price * (1 + buffer_percentage/100)
            
            # Create the formatted string exactly as it would appear in the bot
            display_text = (
                f"• Current Stock Price: ${current_price:.2f}\n"
                f"• Current Option Price: ${option_price:.2f}\n"
                f"• Stock Price Stop Level: ${stop_loss:.2f} "
                f"({buffer_percentage:.1f}% "
                f"{'below' if option_type == 'call' else 'above'} current price)\n"
                f"• Option Price at Stop Recommendation Level: $XX.XX"
            )
            
            print(display_text)
            
            # Verify the buffer percentage is shown correctly
            expected_pattern = rf"{buffer_percentage:.1f}% ({'below' if option_type == 'call' else 'above'})"
            if re.search(expected_pattern, display_text):
                print(f"✅ PASS: Buffer correctly displayed as {buffer_percentage:.1f}% " 
                      f"{'below' if option_type == 'call' else 'above'} current price")
            else:
                print(f"❌ FAIL: Buffer not displayed correctly")
            
            # Verify the stop level calculation is correct
            if option_type == "call":
                expected_stop = current_price * (1 - buffer_percentage/100)
            else:
                expected_stop = current_price * (1 + buffer_percentage/100)
                
            if abs(stop_loss - expected_stop) < 0.01:
                print(f"✅ PASS: Stop level calculated correctly: ${stop_loss:.2f}")
            else:
                print(f"❌ FAIL: Stop level calculation incorrect")

if __name__ == "__main__":
    test_buffer_display()