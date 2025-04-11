#!/usr/bin/env python3
"""
Script to verify that buffer limits based on DTE are correctly enforced.
This script will manually test the buffer percentage limits for both CALL and PUT options
at different DTE values to ensure they match the expected buffer limits.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from technical_analysis import (
    get_scalp_stop_loss,
    get_swing_stop_loss,
    get_longterm_stop_loss
)

def test_buffer_limits():
    """Test buffer limits for different DTE values"""
    print("Testing Buffer Limits by DTE")
    print("===========================")
    
    # Use a stable stock for testing
    ticker_symbol = "AAPL"
    stock = yf.Ticker(ticker_symbol)
    current_price = 175.0  # Use fixed price for consistent testing
    
    # DTE values to test
    dte_values = [1, 2, 4, 10, 90]
    
    print("\nExpected Buffer Limits (CALL options):")
    print("- 1.0% for 0-1 DTE")
    print("- 2.0% for 2 DTE")
    print("- 3.0% for 3-5 DTE") 
    print("- 5.0% for 6-60 DTE")
    print("- 5.0% for 60+ DTE")
    
    print("\nExpected Buffer Limits (PUT options):")
    print("- 1.0% for 0-1 DTE")
    print("- 2.0% for 2 DTE")
    print("- 3.0% for 3-5 DTE")
    print("- 5.0% for 6-60 DTE") 
    print("- 7.0% for 60+ DTE")
    
    print("\nTesting CALL Option Buffer Limits:")
    print("--------------------------------")
    for dte in dte_values:
        print(f"\n[DTE = {dte}]")
        
        # Get stop-loss for a CALL option
        try:
            # Determine which function to use based on DTE
            if dte <= 5:
                stop_loss = get_scalp_stop_loss(stock, current_price, "call", days_to_expiration=dte)
            elif dte <= 60:
                stop_loss = get_swing_stop_loss(stock, current_price, "call", days_to_expiration=dte)
            else:
                stop_loss = get_longterm_stop_loss(stock, current_price, "call", days_to_expiration=dte)
                
            stop_level = stop_loss["level"]
            
            # Calculate actual percentage drop
            actual_percentage = ((current_price - stop_level) / current_price) * 100
            
            # Define expected percentage based on DTE
            if dte <= 1:
                expected_percentage = 1.0
            elif dte == 2:
                expected_percentage = 2.0
            elif dte <= 5:
                expected_percentage = 3.0
            else:
                expected_percentage = 5.0  # Max for CALL options
            
            print(f"Stop Level: ${stop_level:.2f}")
            print(f"Percentage Drop: {actual_percentage:.2f}%")
            print(f"Expected Max Percentage: {expected_percentage:.1f}%")
            
            # Check if the drop is less than or equal to expected percentage
            # Note: Actual percentage could be smaller due to technical level being closer to current price
            if actual_percentage <= expected_percentage * 1.1:  # Allow 10% tolerance
                print("✓ PASS: Buffer limit respected")
            else:
                print("✗ FAIL: Buffer limit exceeded")
                
        except Exception as e:
            print(f"Error calculating stop loss: {e}")
    
    print("\nTesting PUT Option Buffer Limits:")
    print("--------------------------------")
    for dte in dte_values:
        print(f"\n[DTE = {dte}]")
        
        # Get stop-loss for a PUT option
        try:
            # Determine which function to use based on DTE
            if dte <= 5:
                stop_loss = get_scalp_stop_loss(stock, current_price, "put", days_to_expiration=dte)
            elif dte <= 60:
                stop_loss = get_swing_stop_loss(stock, current_price, "put", days_to_expiration=dte)
            else:
                stop_loss = get_longterm_stop_loss(stock, current_price, "put", days_to_expiration=dte)
                
            stop_level = stop_loss["level"]
            
            # Calculate actual percentage rise
            actual_percentage = ((stop_level - current_price) / current_price) * 100
            
            # Define expected percentage based on DTE
            if dte <= 1:
                expected_percentage = 1.0
            elif dte == 2:
                expected_percentage = 2.0
            elif dte <= 5:
                expected_percentage = 3.0
            elif dte <= 60:
                expected_percentage = 5.0
            else:
                expected_percentage = 7.0  # Max for PUT options for long-term
            
            print(f"Stop Level: ${stop_level:.2f}")
            print(f"Percentage Rise: {actual_percentage:.2f}%")
            print(f"Expected Max Percentage: {expected_percentage:.1f}%")
            
            # Check if the rise is less than or equal to expected percentage
            # Note: Actual percentage could be smaller due to technical level being closer to current price
            if actual_percentage <= expected_percentage * 1.1:  # Allow 10% tolerance
                print("✓ PASS: Buffer limit respected")
            else:
                print("✗ FAIL: Buffer limit exceeded")
                
        except Exception as e:
            print(f"Error calculating stop loss: {e}")

if __name__ == "__main__":
    test_buffer_limits()