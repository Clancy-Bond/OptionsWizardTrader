"""
Test script for the enhanced option price calculator.
This script compares the delta approximation method with the full Black-Scholes recalculation
for various option scenarios, with particular focus on at-the-money options near expiration.
"""

import option_price_calculator as opc
from datetime import datetime, timedelta

def test_near_expiration_options():
    """
    Test the calculator on near-expiration options where delta approximation often fails.
    """
    print("TESTING NEAR-EXPIRATION OPTIONS")
    print("===============================")
    
    # Test parameters
    current_stock_price = 500.00
    strike_price = 500.00  # ATM option
    current_option_price = 5.00
    implied_volatility = 0.30
    option_type = 'put'
    
    # Test various days to expiration
    days_list = [0, 1, 2, 5, 10, 30]
    
    # Test different stop loss levels (percentage buffer from current price)
    buffer_percentages = [0.5, 1.0, 2.0, 3.0, 5.0]
    
    print(f"{option_type.upper()} OPTION AT ${strike_price:.2f} STRIKE (CURRENT STOCK: ${current_stock_price:.2f})")
    print(f"Current option price: ${current_option_price:.2f}")
    print()
    
    for days in days_list:
        print(f"{days} DAYS TO EXPIRATION")
        print("------------------------")
        
        # Table header
        print("{:<8} {:<13} {:<20} {:<20} {:<15}".format(
            "Buffer", "Stop Level", "Delta Approximation", "Black-Scholes", "Difference"))
        print("-" * 80)
        
        for buffer in buffer_percentages:
            # Calculate stop loss level based on buffer
            if option_type.lower() == 'call':
                stop_level = current_stock_price * (1 - buffer/100)
            else:
                stop_level = current_stock_price * (1 + buffer/100)
            
            # For extremely short-dated options, we need a delta estimate
            # This would normally come from market data, but we'll estimate for the test
            delta_estimate = 0.5 if option_type.lower() == 'call' else -0.5
            
            # Calculate using delta approximation
            price_delta_approx = opc.calculate_option_price_at_stop(
                current_option_price, 
                current_stock_price, 
                stop_level, 
                strike_price,
                days,
                implied_volatility,
                option_type,
                use_full_bs=False,
                delta=delta_estimate
            )
            
            # Calculate using full Black-Scholes
            price_full_bs = opc.calculate_option_price_at_stop(
                current_option_price, 
                current_stock_price, 
                stop_level, 
                strike_price,
                days,
                implied_volatility,
                option_type,
                use_full_bs=True
            )
            
            # Calculate percentage changes
            pct_change_delta = opc.calculate_percentage_change(current_option_price, price_delta_approx)
            pct_change_bs = opc.calculate_percentage_change(current_option_price, price_full_bs)
            
            # Format for display
            delta_display = f"${price_delta_approx:.2f} ({pct_change_delta:.1f}%)"
            bs_display = f"${price_full_bs:.2f} ({pct_change_bs:.1f}%)"
            diff_display = f"{abs(price_delta_approx - price_full_bs):.2f} ({abs(pct_change_delta - pct_change_bs):.1f}%)"
            
            print("{:<8.1f}% {:<13.2f} {:<20} {:<20} {:<15}".format(
                buffer, stop_level, delta_display, bs_display, diff_display
            ))
        
        print()

def test_specific_spy_case():
    """
    Test the specific SPY case from our previous investigation.
    SPY PUT at $496 with stock price at $496.48 on expiration day.
    """
    print("SPY EXPIRATION DAY PUT TEST")
    print("==========================")
    
    # Parameters from the screenshot
    current_stock_price = 496.48
    strike_price = 496.00
    current_option_price = 8.83
    implied_volatility = 0.35  # Estimated
    option_type = 'put'
    days_to_expiration = 0  # Same-day expiration
    stop_loss_level = 501.44  # From the screenshot (1.0% buffer)
    delta_estimate = -0.40  # Estimated delta for this position
    
    print(f"SPY PUT at ${strike_price:.2f} strike")
    print(f"Current stock price: ${current_stock_price:.2f}")
    print(f"Current option price: ${current_option_price:.2f}")
    print(f"Stop loss level: ${stop_loss_level:.2f} (1.0% buffer)")
    print(f"Estimated delta: {delta_estimate:.4f}")
    print()
    
    # Delta approximation calculation
    price_delta_approx = opc.calculate_option_price_at_stop(
        current_option_price, 
        current_stock_price, 
        stop_loss_level, 
        strike_price,
        days_to_expiration,
        implied_volatility,
        option_type,
        use_full_bs=False,
        delta=delta_estimate
    )
    
    # Full BS calculation
    price_full_bs = opc.calculate_option_price_at_stop(
        current_option_price, 
        current_stock_price, 
        stop_loss_level, 
        strike_price,
        days_to_expiration,
        implied_volatility,
        option_type,
        use_full_bs=True
    )
    
    # Alternative calculation with 0.1 days
    price_full_bs_alt = opc.calculate_option_price_at_stop(
        current_option_price, 
        current_stock_price, 
        stop_loss_level, 
        strike_price,
        0.1,  # Small positive DTE
        implied_volatility,
        option_type,
        use_full_bs=True
    )
    
    # Calculate percentage changes
    pct_change_delta = opc.calculate_percentage_change(current_option_price, price_delta_approx)
    pct_change_bs = opc.calculate_percentage_change(current_option_price, price_full_bs)
    pct_change_bs_alt = opc.calculate_percentage_change(current_option_price, price_full_bs_alt)
    
    print("OPTION PRICE AT STOP LOSS LEVEL:")
    print(f"Delta approximation: ${price_delta_approx:.2f} ({pct_change_delta:.1f}% {'loss' if pct_change_delta < 0 else 'gain'})")
    print(f"Black-Scholes 0 DTE: ${price_full_bs:.2f} ({pct_change_bs:.1f}% {'loss' if pct_change_bs < 0 else 'gain'})")
    print(f"Black-Scholes 0.1 DTE: ${price_full_bs_alt:.2f} ({pct_change_bs_alt:.1f}% {'loss' if pct_change_bs_alt < 0 else 'gain'})")
    print()
    
    # Test various buffer percentages
    print("TESTING DIFFERENT BUFFER PERCENTAGES (0.1 DTE):")
    buffer_percentages = [0.5, 1.0, 2.0, 3.0, 5.0]
    
    # Table header
    print("{:<8} {:<13} {:<20} {:<20} {:<15}".format(
        "Buffer", "Stop Level", "Delta Approximation", "Black-Scholes", "Difference"))
    print("-" * 80)
    
    for buffer in buffer_percentages:
        # Calculate stop loss level based on buffer
        stop_level = current_stock_price * (1 + buffer/100)
        
        # Calculate using delta approximation
        delta_price = opc.calculate_option_price_at_stop(
            current_option_price, 
            current_stock_price, 
            stop_level, 
            strike_price,
            0.1,  # Using small positive DTE
            implied_volatility,
            option_type,
            use_full_bs=False,
            delta=delta_estimate
        )
        
        # Calculate using full Black-Scholes
        bs_price = opc.calculate_option_price_at_stop(
            current_option_price, 
            current_stock_price, 
            stop_level, 
            strike_price,
            0.1,  # Using small positive DTE
            implied_volatility,
            option_type,
            use_full_bs=True
        )
        
        # Calculate percentage changes
        delta_pct = opc.calculate_percentage_change(current_option_price, delta_price)
        bs_pct = opc.calculate_percentage_change(current_option_price, bs_price)
        
        # Format for display
        delta_display = f"${delta_price:.2f} ({delta_pct:.1f}%)"
        bs_display = f"${bs_price:.2f} ({bs_pct:.1f}%)"
        diff_display = f"${abs(delta_price - bs_price):.2f} ({abs(delta_pct - bs_pct):.1f}%)"
        
        print("{:<8.1f}% {:<13.2f} {:<20} {:<20} {:<15}".format(
            buffer, stop_level, delta_display, bs_display, diff_display
        ))

if __name__ == "__main__":
    # test_near_expiration_options()
    # print("\n" + "=" * 80 + "\n")
    test_specific_spy_case()