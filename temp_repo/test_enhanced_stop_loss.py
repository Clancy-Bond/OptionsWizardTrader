"""
Test script to validate the enhanced ATR-based stop loss system

This script creates test cases for various option types, timeframes,
and validates that the stop loss recommendations include the enhanced features:
- Pattern recognition (breakout/engulfing)
- Volume confirmation (≥ 1.5x average of last 10 candles) 
- ATR-based buffers (10% for breakouts, 5% for engulfing)
- Support/resistance validation
"""

import yfinance as yf
import pandas as pd
import numpy as np
from technical_analysis import get_stop_loss_recommendation
from enhanced_atr_stop_loss import (
    calculate_breakout_stop_loss,
    calculate_engulfing_stop_loss,
    get_enhanced_stop_loss
)

def test_enhanced_stop_loss():
    """Test the enhanced ATR-based stop loss system with real market data"""
    
    # Test cases - different stocks, option types, and timeframes
    test_cases = [
        {"ticker": "AAPL", "option_type": "call", "days": 7, "name": "AAPL 7-day call"},
        {"ticker": "MSFT", "option_type": "put", "days": 30, "name": "MSFT 30-day put"},
        {"ticker": "TSLA", "option_type": "call", "days": 60, "name": "TSLA 60-day call"},
        {"ticker": "AMZN", "option_type": "put", "days": 2, "name": "AMZN 2-day put"}
    ]
    
    for test in test_cases:
        print(f"\n=== Testing {test['name']} ===")
        
        # Get stock data
        stock = yf.Ticker(test["ticker"])
        current_price = stock.history(period="1d")["Close"].iloc[-1]
        
        # Calculate expiration date
        import datetime
        today = datetime.datetime.now().date()
        expiry = today + datetime.timedelta(days=test["days"])
        expiry_str = expiry.strftime("%Y-%m-%d")
        
        print(f"Current price: ${current_price:.2f}, Expiration: {expiry_str}")
        
        # Get direct pattern-based recommendations
        print("\nTesting direct pattern detection:")
        breakout = calculate_breakout_stop_loss(stock, current_price, test["option_type"], test["days"])
        if breakout:
            print(f"✓ Breakout pattern found: {breakout['direction']} {breakout['pattern']}")
            print(f"  Stop level: ${breakout['level']:.2f}")
            print(f"  Volume confirmation: {breakout.get('volume_confirmed', False)}")
            print(f"  At key level: {breakout.get('at_key_level', False)}")
        else:
            print("✗ No breakout pattern detected")
        
        engulfing = calculate_engulfing_stop_loss(stock, current_price, test["option_type"], test["days"])
        if engulfing:
            print(f"✓ Engulfing pattern found: {engulfing['direction']} {engulfing['pattern']}")
            print(f"  Stop level: ${engulfing['level']:.2f}")
            print(f"  Volume confirmation: {engulfing.get('volume_confirmed', False)}")
            print(f"  At key level: {engulfing.get('at_key_level', False)}")
        else:
            print("✗ No engulfing pattern detected")
        
        # Get enhanced stop loss recommendation
        enhanced = get_enhanced_stop_loss(stock, current_price, test["option_type"], test["days"])
        if enhanced:
            print(f"✓ Enhanced stop loss recommendation found")
            print(f"  Pattern: {enhanced['pattern']}")
            print(f"  Direction: {enhanced['direction']}")
            print(f"  Stop level: ${enhanced['level']:.2f}")
            print(f"  Time horizon: {enhanced['time_horizon']}")
        else:
            print("✗ No enhanced stop loss recommendation found")
        
        # Get comprehensive recommendations via technical_analysis
        result = get_stop_loss_recommendation(stock, current_price, test["option_type"], expiry_str)
        
        # Check if enhanced recommendations are included
        if "enhanced" in result:
            print(f"\n✓ Enhanced stop loss included in comprehensive recommendation")
            print(f"  Pattern: {result['enhanced']['pattern']}")
            print(f"  Stop level: ${result['enhanced']['level']:.2f}")
        else:
            print("\n✗ No enhanced stop loss in comprehensive recommendation")
        
        # Check if primary recommendation uses enhanced when available
        if "primary" in result and "enhanced" in result:
            uses_enhanced = result["primary"] == result["enhanced"]
            print(f"  Primary recommendation uses enhanced: {uses_enhanced}")
        
        print("\nTime horizon recommendations:")
        for horizon in ["scalp", "swing", "longterm"]:
            if horizon in result and result[horizon]:
                print(f"  {horizon.capitalize()}: ${result[horizon]['level']:.2f}")

if __name__ == "__main__":
    test_enhanced_stop_loss()