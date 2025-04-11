"""
Detailed debugging script for technical analysis components
"""
import os
import sys
import yfinance as yf
import numpy as np
from datetime import datetime
import traceback

# Add current directory to path
sys.path.append('.')

# Import from technical_analysis
try:
    from technical_analysis import (
        get_stop_loss_recommendation,
        get_stop_loss_recommendations,
        get_swing_stop_loss,
        get_support_levels,
        calculate_atr
    )
except ImportError as e:
    print(f"Error importing from technical_analysis: {e}")
    sys.exit(1)

def debug_stop_loss_recommendation():
    """
    Debug the specific TSLA query in extreme detail
    """
    try:
        # Parameters from the user query
        # Test both CALL and PUT options with current dates
        tests = [
            {"ticker": "TSLA", "option_type": "call", "expiration": "2025-05-02", "desc": "TSLA CALL (24 DTE)"},
            {"ticker": "TSLA", "option_type": "put", "expiration": "2025-05-02", "desc": "TSLA PUT (24 DTE)"},
            {"ticker": "SPY", "option_type": "call", "expiration": "2025-04-09", "desc": "SPY CALL (1 DTE)"}
        ]
        
        for test in tests:
            ticker_symbol = test["ticker"]
            option_type = test["option_type"]
            expiration_date = test["expiration"]
            print(f"\n\n===== TESTING {test['desc']} =====\n")
            
            # Get the stock data
            print(f"Fetching data for {ticker_symbol}...")
            stock = yf.Ticker(ticker_symbol)
            current_price = stock.history(period="1d")['Close'].iloc[-1]
            print(f"Current {ticker_symbol} price: ${current_price:.2f}")
            
            # Calculate days to expiration
            expiry_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
            today = datetime.now().date()
            days_to_expiration = (expiry_date - today).days
            print(f"Days to expiration: {days_to_expiration}")
            
            # STAGE 1: Support/Resistance Analysis
            if option_type == "call":
                print("\n=== STAGE 1: Support Level Analysis (for CALL) ===")
                support_levels = get_support_levels(stock, periods=[14, 30])
                valid_supports = [level for level in support_levels if level < current_price]
                print(f"All support levels: {[f'${level:.2f}' for level in support_levels]}")
                print(f"Valid supports below current price: {[f'${level:.2f}' for level in valid_supports]}")
                
                if valid_supports:
                    highest_support = valid_supports[0]
                    print(f"Highest support level: ${highest_support:.2f}")
                    print(f"Support distance from current price: ${current_price - highest_support:.2f} ({((current_price - highest_support) / current_price) * 100:.2f}%)")
                else:
                    print("No valid supports found below current price.")
            else:
                print("\n=== STAGE 1: Resistance Level Analysis (for PUT) ===")
                # For PUT options, we're interested in resistance levels above current price
                resistance_levels = []
                for period in [14, 30]:
                    hist = stock.history(period=f"{period}d")
                    if not hist.empty:
                        order = min(5, len(hist) // 10)
                        if order > 0:
                            from scipy.signal import argrelextrema
                            local_max_indices = argrelextrema(hist['High'].values, np.greater, order=order)[0]
                            resistance_prices = hist['High'].iloc[local_max_indices].values
                            resistance_levels.extend(resistance_prices)
                
                valid_resistances = [level for level in resistance_levels if level > current_price]
                valid_resistances = sorted(valid_resistances)
                
                print(f"Found resistance levels: {[f'${level:.2f}' for level in resistance_levels]}")
                print(f"Valid resistances above current price: {[f'${level:.2f}' for level in valid_resistances]}")
                
                if valid_resistances:
                    lowest_resistance = valid_resistances[0]
                    print(f"Closest resistance level: ${lowest_resistance:.2f}")
                    print(f"Resistance distance from current price: ${lowest_resistance - current_price:.2f} ({((lowest_resistance - current_price) / current_price) * 100:.2f}%)")
                else:
                    print("No valid resistances found above current price.")
            
            # STAGE 2: ATR Calculation
            print("\n=== STAGE 2: Volatility Analysis ===")
            # Try different intervals to see what's working
            intervals = ["4h", "1d"]
            
            for interval in intervals:
                print(f"\nTrying {interval} interval...")
                try:
                    hist_data = stock.history(period="7d" if interval == "4h" else "30d", interval=interval)
                    if hist_data.empty:
                        print(f"No {interval} data available.")
                        continue
                        
                    print(f"Got {len(hist_data)} candles for {interval} interval.")
                    atr = calculate_atr(hist_data, window=14)  # Standard 14-period ATR
                    print(f"ATR value: ${atr:.2f}")
                    print(f"ATR as percentage of price: {(atr / current_price) * 100:.2f}%")
                    
                    # Simulate different ATR multiples
                    print("\nPotential stop levels with different ATR multiples:")
                    for multiple in [0.5, 1.0, 1.5, 2.0]:
                        if option_type == "call":
                            potential_stop = current_price - (multiple * atr)
                            buffer_pct = ((current_price - potential_stop) / current_price) * 100
                            print(f"{multiple}x ATR: ${potential_stop:.2f} ({buffer_pct:.2f}% below current price)")
                        else:
                            potential_stop = current_price + (multiple * atr)
                            buffer_pct = ((potential_stop - current_price) / current_price) * 100
                            print(f"{multiple}x ATR: ${potential_stop:.2f} ({buffer_pct:.2f}% above current price)")
                    
                except Exception as e:
                    print(f"Error analyzing {interval} data: {str(e)}")
            
            # STAGE 3: Full stop loss calculation 
            print("\n=== STAGE 3: Full Stop Loss Calculation ===")
            result = get_stop_loss_recommendations(ticker_symbol, current_price, option_type, expiration_date)
            
            print("\nTrade horizon detected:", result.get("trade_horizon", "unknown"))
            
            # Check what's in the result
            print("\nKeys in result:", result.keys())
            
            # Display primary recommendation
            if "primary" in result:
                primary = result["primary"]
                print("\nPRIMARY RECOMMENDATION:")
                print(f"Stop level: ${primary['level']:.2f}")
                if option_type == "call":
                    pct_change = ((current_price - primary['level']) / current_price) * 100
                    print(f"Percentage change: {pct_change:.2f}% below current price")
                else:
                    pct_change = ((primary['level'] - current_price) / current_price) * 100
                    print(f"Percentage change: {pct_change:.2f}% above current price")
                print(f"Recommendation text: {primary['recommendation']}")
                
            # Check for swing recommendation specifically
            if "swing" in result:
                swing = result["swing"]
                print("\nSWING RECOMMENDATION:")
                print(f"Stop level: ${swing['level']:.2f}")
                if option_type == "call":
                    pct_change = ((current_price - swing['level']) / current_price) * 100
                    print(f"Percentage change: {pct_change:.2f}% below current price")
                else:
                    pct_change = ((swing['level'] - current_price) / current_price) * 100
                    print(f"Percentage change: {pct_change:.2f}% above current price")
                print(f"Recommendation text: {swing['recommendation']}")
            
            # STAGE 4: Direct Swing Stop Loss Analysis
            print("\n=== STAGE 4: Direct Swing Stop Loss Analysis ===")
            swing_result = get_swing_stop_loss(stock, current_price, option_type, days_to_expiration)
            
            print("\nRAW SWING CALCULATION:")
            print(f"Stop level: ${swing_result['level']:.2f}")
            if option_type == "call":
                pct_change = ((current_price - swing_result['level']) / current_price) * 100
                print(f"Percentage change: {pct_change:.2f}% below current price")
            else:
                pct_change = ((swing_result['level'] - current_price) / current_price) * 100
                print(f"Percentage change: {pct_change:.2f}% above current price")
            print(f"Recommendation text: {swing_result['recommendation']}")
            
            # STAGE 5: Buffer Limit Analysis
            print("\n=== STAGE 5: Buffer Limit Analysis ===")
            if option_type == "call":
                if days_to_expiration <= 1:
                    max_buffer_pct = 1.0
                elif days_to_expiration <= 2:
                    max_buffer_pct = 2.0
                elif days_to_expiration <= 5:
                    max_buffer_pct = 3.0
                else:
                    max_buffer_pct = 5.0
                    
                print(f"For a {days_to_expiration} DTE {option_type} option, maximum buffer is {max_buffer_pct}%")
                max_buffer_stop = current_price * (1 - max_buffer_pct/100)
                print(f"{max_buffer_pct}% buffer stop: ${max_buffer_stop:.2f}")
                
                # Compare to calculated stop
                actual_stop = swing_result['level']
                actual_buffer = ((current_price - actual_stop) / current_price) * 100
                print(f"Calculated stop: ${actual_stop:.2f} ({actual_buffer:.2f}%)")
                
                if abs(actual_buffer - max_buffer_pct) < 0.1:  # Within 0.1% of max buffer
                    print(f"Analysis: The calculated stop appears to be right at the {max_buffer_pct}% buffer limit.")
                    print("This suggests either:")
                    print(f"1. Technical analysis found a stop > {max_buffer_pct}% away and was capped at {max_buffer_pct}%")
                    print(f"2. Technical analysis could not find valid levels and defaulted to {max_buffer_pct}%")
                    print(f"3. Technical analysis genuinely found a level that happens to be almost exactly {max_buffer_pct}% away")
                    
                elif actual_buffer < max_buffer_pct:
                    print(f"Analysis: The calculated stop is tighter than the {max_buffer_pct}% buffer limit.")
                    print(f"This suggests technical analysis found a valid support level closer than {max_buffer_pct}%.")
                    
                else:
                    print(f"Analysis: The calculated stop exceeds the {max_buffer_pct}% buffer limit.")
                    print("This suggests a bug in the buffer enforcement mechanism.")
            else:
                if days_to_expiration <= 1:
                    max_buffer_pct = 1.0
                elif days_to_expiration <= 2:
                    max_buffer_pct = 2.0
                elif days_to_expiration <= 5:
                    max_buffer_pct = 3.0
                else:
                    max_buffer_pct = 5.0
                    
                print(f"For a {days_to_expiration} DTE {option_type} option, maximum buffer is {max_buffer_pct}%")
                max_buffer_stop = current_price * (1 + max_buffer_pct/100)
                print(f"{max_buffer_pct}% buffer stop: ${max_buffer_stop:.2f}")
                
                # Compare to calculated stop
                actual_stop = swing_result['level']
                actual_buffer = ((actual_stop - current_price) / current_price) * 100
                print(f"Calculated stop: ${actual_stop:.2f} ({actual_buffer:.2f}%)")
                
                if abs(actual_buffer - max_buffer_pct) < 0.1:  # Within 0.1% of max buffer
                    print(f"Analysis: The calculated stop appears to be right at the {max_buffer_pct}% buffer limit.")
                    print("This suggests either:")
                    print(f"1. Technical analysis found a stop > {max_buffer_pct}% away and was capped at {max_buffer_pct}%")
                    print(f"2. Technical analysis could not find valid levels and defaulted to {max_buffer_pct}%")
                    print(f"3. Technical analysis genuinely found a level that happens to be almost exactly {max_buffer_pct}% away")
                    
                elif actual_buffer < max_buffer_pct:
                    print(f"Analysis: The calculated stop is tighter than the {max_buffer_pct}% buffer limit.")
                    print(f"This suggests technical analysis found a valid resistance level closer than {max_buffer_pct}%.")
                    
                else:
                    print(f"Analysis: The calculated stop exceeds the {max_buffer_pct}% buffer limit.")
                    print("This suggests a bug in the buffer enforcement mechanism.")
        
    except Exception as e:
        print(f"Error in debug_stop_loss_recommendation: {str(e)}")
        traceback.print_exc()

def main():
    debug_stop_loss_recommendation()

if __name__ == "__main__":
    main()