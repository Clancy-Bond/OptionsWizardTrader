"""
Simple test for the theta decay display formatting in option_calculator.py
"""

import datetime
from option_calculator import calculate_theta_decay, calculate_expiry_theta_decay

def test_theta_decay_formatting():
    """Test the formatting of theta decay output for different time periods"""
    print("\n=== Testing theta decay formatting ===")
    
    # Set up test values for our functions
    current_option_price = 5.25  # Current option price
    theta = -0.05  # Daily decay value (negative for time decay)
    
    # Test for different trade horizons
    test_cases = [
        {"name": "SCALP TRADE", "days": 3, "interval": 1},    # Daily intervals
        {"name": "SWING TRADE", "days": 14, "interval": 2},   # 2-day intervals
        {"name": "POSITION TRADE", "days": 45, "interval": 7}, # Weekly intervals
        {"name": "LEAPS OPTION", "days": 180, "interval": 7}  # Weekly intervals
    ]
    
    for case in test_cases:
        print(f"\n--- {case['name']} theta decay ---")
        expiration_date = (datetime.datetime.now() + datetime.timedelta(days=case["days"])).strftime('%Y-%m-%d')
        
        # Test regular theta decay (1 day ahead by default)
        theta_decay = calculate_theta_decay(current_option_price, theta)
        print(f"Regular theta decay (1 day): {theta_decay['warning_message']}")
        
        # Test regular theta decay (3 days ahead)
        theta_decay = calculate_theta_decay(current_option_price, theta, days_ahead=3)
        print(f"Regular theta decay (3 days): {theta_decay['warning_message']}")
        
        # Test expiry theta decay with appropriate interval
        expiry_decay = calculate_expiry_theta_decay(
            current_option_price, 
            theta, 
            expiration_date,
            max_days=case["days"],
            interval=case["interval"]
        )
        
        print(f"Expiry theta decay for {case['name']}:")
        print(f"Warning status: {expiry_decay['warning_status']}")
        print(f"Warning message: {expiry_decay['warning_message'][:100]}...")  # Show just the first 100 chars

if __name__ == "__main__":
    test_theta_decay_formatting()