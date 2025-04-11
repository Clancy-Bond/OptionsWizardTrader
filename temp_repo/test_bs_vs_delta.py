"""
Test script comparing delta approximation vs full Black-Scholes recalculation
for option price changes, especially for ATM options near expiration.
"""

import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta

def black_scholes(S, K, T, r, sigma, option_type='call'):
    """
    Calculate option price using Black-Scholes formula.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration in years
        r: Risk-free rate
        sigma: Implied volatility
        option_type: 'call' or 'put'
        
    Returns:
        Option price
    """
    if T <= 0:
        # Handle zero or negative time to expiration
        if option_type.lower() == 'call':
            return max(0, S - K)
        else:
            return max(0, K - S)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type.lower() == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return price

def calculate_option_greeks(S, K, T, r, sigma, option_type='call'):
    """
    Calculate option Greeks using Black-Scholes.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration in years
        r: Risk-free rate
        sigma: Implied volatility
        option_type: 'call' or 'put'
        
    Returns:
        Dictionary with delta, gamma, theta, vega, price
    """
    if T <= 0:
        # Handle zero or negative time to expiration
        if option_type.lower() == 'call':
            return {
                'delta': 1.0 if S > K else 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'price': max(0, S - K)
            }
        else:
            return {
                'delta': -1.0 if S < K else 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'price': max(0, K - S)
            }
    
    try:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        price = black_scholes(S, K, T, r, sigma, option_type)
        
        if option_type.lower() == 'call':
            delta = norm.cdf(d1)
            theta = -((S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))) - r * K * np.exp(-r * T) * norm.cdf(d2)
        else:
            delta = norm.cdf(d1) - 1
            theta = -((S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))) + r * K * np.exp(-r * T) * norm.cdf(-d2)
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * np.sqrt(T) * norm.pdf(d1) * 0.01  # Multiply by 0.01 to get the impact of a 1% change in volatility
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta / 365.0,  # Convert to daily theta
            'vega': vega,
            'price': price
        }
    except Exception as e:
        print(f"Error calculating Greeks: {str(e)}")
        return {
            'delta': 0.0,
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0,
            'price': 0.0
        }

def delta_approximation(option_price, stock_price, target_price, delta, option_type):
    """
    Calculate option price change using delta approximation.
    
    Args:
        option_price: Current option price
        stock_price: Current stock price
        target_price: Target stock price
        delta: Option delta
        option_type: 'call' or 'put'
        
    Returns:
        Estimated option price at target stock price
    """
    price_change = target_price - stock_price
    
    if option_type.lower() == 'call':
        option_price_change = price_change * abs(delta)
    else:
        option_price_change = -price_change * abs(delta)  # For puts, price goes down when stock goes up
    
    return max(0.01, option_price + option_price_change)

def test_atm_option_near_expiration():
    """
    Test delta approximation vs full BS recalculation for ATM options near expiration.
    """
    print("TESTING ATM OPTIONS NEAR EXPIRATION")
    print("===================================")
    
    # Base parameters
    current_stock_price = 500.0
    strike_price = 500.0  # ATM
    risk_free_rate = 0.05
    implied_volatility = 0.25
    option_type = 'put'  # Testing PUT options
    
    # Test different days to expiration
    days_list = [0, 1, 2, 5, 10, 30]
    
    # Test different stop loss buffers (percentage of stock price)
    buffer_percentages = [0.5, 1.0, 2.0, 3.0, 5.0]
    
    # Print header
    print(f"{option_type.upper()} OPTION AT ${strike_price:.2f} STRIKE (CURRENT STOCK: ${current_stock_price:.2f})")
    print("\nCOMPARISON OF DELTA APPROXIMATION VS FULL BLACK-SCHOLES RECALCULATION")
    print("------------------------------------------------------------------")
    
    for days_to_expiration in days_list:
        print(f"\n{days_to_expiration} DAYS TO EXPIRATION")
        print("------------------------")
        
        # Calculate time to expiration in years
        T = days_to_expiration / 365.0
        
        # Calculate option price and Greeks
        greeks = calculate_option_greeks(current_stock_price, strike_price, T, risk_free_rate, implied_volatility, option_type)
        current_option_price = greeks['price']
        delta = greeks['delta']
        
        print(f"Option Price: ${current_option_price:.2f}, Delta: {delta:.4f}")
        
        # Table header
        print("\n{:<8} {:<13} {:<12} {:<12} {:<12} {:<12} {:<12}".format(
            "Buffer", "Stop Level", "Delta Approx", "BS Price", "Difference", "Delta Loss %", "BS Loss %"))
        print("-" * 80)
        
        for buffer_pct in buffer_percentages:
            # Calculate stop loss level based on buffer
            if option_type.lower() == 'call':
                stop_loss_level = current_stock_price * (1 - buffer_pct/100)
            else:
                stop_loss_level = current_stock_price * (1 + buffer_pct/100)
            
            # Delta approximation
            delta_approx_price = delta_approximation(
                current_option_price, current_stock_price, stop_loss_level, delta, option_type
            )
            
            # Full Black-Scholes recalculation
            bs_price = black_scholes(
                stop_loss_level, strike_price, T, risk_free_rate, implied_volatility, option_type
            )
            
            # Calculate loss percentages
            if current_option_price > 0:
                delta_loss_pct = (delta_approx_price - current_option_price) / current_option_price * 100
                bs_loss_pct = (bs_price - current_option_price) / current_option_price * 100
            else:
                # Handle edge case where current option price is zero
                delta_loss_pct = 0.0
                bs_loss_pct = 0.0
            
            # Calculate absolute difference
            difference = abs(delta_approx_price - bs_price)
            
            # Format and print results
            print("{:<8.1f}% {:<13.2f} {:<12.2f} {:<12.2f} {:<12.2f} {:<12.1f}% {:<12.1f}%".format(
                buffer_pct, stop_loss_level, delta_approx_price, bs_price, difference, delta_loss_pct, bs_loss_pct
            ))

def test_specific_spy_case():
    """
    Test the specific SPY case from the screenshot:
    SPY PUT at $496 with stock price at $496.48 on expiration day
    """
    print("\n\nSPECIFIC SPY CASE FROM SCREENSHOT")
    print("=================================")
    
    # Parameters from the screenshot
    current_stock_price = 496.48
    strike_price = 496.00
    option_price = 8.83
    risk_free_rate = 0.05
    implied_volatility = 0.35  # Try a higher IV level
    option_type = 'put'
    days_to_expiration = 0  # Same-day expiration
    
    # Test different buffer levels: 0.5%, 1.0%, and 2.0%
    buffer_percentages = [0.5, 1.0, 2.0]
    stop_loss_level = 501.44  # From the screenshot (1.0% buffer)
    
    # We'll also test with a small positive time to expiration
    alternative_days = 0.1  # Just a small fraction of a day
    
    # Calculate time to expiration in years
    T = days_to_expiration / 365.0
    
    # Calculate option price and Greeks
    greeks = calculate_option_greeks(current_stock_price, strike_price, T, risk_free_rate, implied_volatility, option_type)
    
    # Use the actual option price from the screenshot
    delta = greeks['delta']
    
    print(f"SPY PUT at ${strike_price:.2f} strike")
    print(f"Current stock price: ${current_stock_price:.2f}")
    print(f"Stop loss level: ${stop_loss_level:.2f} (1.0% buffer)")
    print(f"Current option price: ${option_price:.2f}")
    print(f"Calculated delta: {delta:.4f}")
    
    # Delta approximation
    delta_approx_price = delta_approximation(
        option_price, current_stock_price, stop_loss_level, delta, option_type
    )
    
    # Full Black-Scholes recalculation
    bs_price = black_scholes(
        stop_loss_level, strike_price, T, risk_free_rate, implied_volatility, option_type
    )
    
    # Calculate loss percentages
    delta_loss_pct = (delta_approx_price - option_price) / option_price * 100
    bs_loss_pct = (bs_price - option_price) / option_price * 100
    
    print("\nResults:")
    print(f"Delta approximation price: ${delta_approx_price:.2f} ({delta_loss_pct:.1f}% {'loss' if delta_loss_pct < 0 else 'gain'})")
    print(f"Black-Scholes price: ${bs_price:.2f} ({bs_loss_pct:.1f}% {'loss' if bs_loss_pct < 0 else 'gain'})")
    print(f"Absolute difference: ${abs(delta_approx_price - bs_price):.2f}")
    
    # Now test with a small positive time to expiration
    print("\nTesting with small positive time to expiration (0.1 days):")
    T_alt = alternative_days / 365.0
    
    # Calculate with the alternative time
    greeks_alt = calculate_option_greeks(current_stock_price, strike_price, T_alt, risk_free_rate, implied_volatility, option_type)
    delta_alt = greeks_alt['delta']
    print(f"Calculated delta: {delta_alt:.4f}")
    
    # Test different buffer percentages
    print("\n{:<10} {:<15} {:<15} {:<15} {:<15}".format(
        "Buffer %", "Stop Level", "Delta Price", "BS Price", "Difference %"))
    print("-" * 70)
    
    for buffer_pct in buffer_percentages:
        # Calculate stop level based on buffer percentage
        stop_level = current_stock_price * (1 + buffer_pct/100)
        
        # Delta approximation with alternative delta
        delta_approx_price = delta_approximation(
            option_price, current_stock_price, stop_level, delta_alt, option_type
        )
        
        # BS recalculation with alternative time
        bs_price = black_scholes(stop_level, strike_price, T_alt, risk_free_rate, implied_volatility, option_type)
        
        # Calculate loss percentages
        delta_loss_pct = (delta_approx_price - option_price) / option_price * 100
        bs_loss_pct = (bs_price - option_price) / option_price * 100
        diff_pct = bs_loss_pct - delta_loss_pct
        
        print("{:<10.1f} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.1f}%".format(
            buffer_pct, stop_level, delta_approx_price, bs_price, diff_pct))
    
    # For comparison, use the specific stop level from screenshot
    delta_approx_price_alt = delta_approximation(
        option_price, current_stock_price, stop_loss_level, delta_alt, option_type
    )
    
    bs_price_alt = black_scholes(stop_loss_level, strike_price, T_alt, risk_free_rate, implied_volatility, option_type)
    
    delta_loss_pct_alt = (delta_approx_price_alt - option_price) / option_price * 100
    bs_loss_pct_alt = (bs_price_alt - option_price) / option_price * 100
    
    # Different IV levels
    print("\nTesting different implied volatility levels:")
    print("{:<10} {:<15} {:<15} {:<15}".format("IV", "BS Price", "BS Loss %", "Loss vs Delta"))
    print("-" * 55)
    
    for iv in [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]:
        bs_price = black_scholes(stop_loss_level, strike_price, T_alt, risk_free_rate, iv, option_type)
        bs_loss_pct = (bs_price - option_price) / option_price * 100
        
        print("{:<10.2f} {:<15.2f} {:<15.1f}% {:<15.1f}%".format(
            iv, bs_price, bs_loss_pct, bs_loss_pct - delta_loss_pct_alt
        ))

if __name__ == "__main__":
    # test_atm_option_near_expiration()  # Comment out to focus on specific case
    test_specific_spy_case()