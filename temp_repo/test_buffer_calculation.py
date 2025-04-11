"""
A simplified test for the dynamic buffer calculations used in stop loss recommendations.
This directly tests the buffer scaling logic without requiring external data.
"""

def get_dynamic_buffer_for_dte(days_to_expiration):
    """
    Calculate the appropriate buffer size based on days to expiration (DTE).
    
    This is the core logic extracted from the stop loss functions:
    - 0-1 DTE: 0.1% buffer
    - 2 DTE: 0.2% buffer
    - 3-5 DTE: 3% buffer
    - 6+ DTE: 5% buffer
    """
    if days_to_expiration <= 1:
        return 0.001  # 0.1%
    elif days_to_expiration == 2:
        return 0.002  # 0.2%
    elif days_to_expiration <= 5:
        return 0.03   # 3%
    else:
        return 0.05   # 5%

def test_dynamic_buffers():
    """
    Test the dynamic buffer calculations for different DTE values.
    """
    # Test cases
    test_cases = [0, 1, 2, 3, 4, 5, 6, 7, 14, 30, 90, 180]
    
    print("\n===== DYNAMIC BUFFER CALCULATIONS =====")
    for dte in test_cases:
        buffer = get_dynamic_buffer_for_dte(dte)
        buffer_pct = buffer * 100  # Convert to percentage
        
        print(f"DTE {dte:3d}: {buffer_pct:4.1f}% buffer")
    
    # Calculate example stop levels for a stock at $500
    current_price = 500.0
    
    print("\n===== EXAMPLE STOP LEVELS FOR CALL OPTIONS =====")
    print(f"Current stock price: ${current_price:.2f}")
    for dte in test_cases:
        buffer = get_dynamic_buffer_for_dte(dte)
        stop_level = current_price * (1 - buffer)
        buffer_pct = buffer * 100
        
        print(f"DTE {dte:3d}: Stop at ${stop_level:.2f} ({buffer_pct:.1f}% below current price)")
    
    print("\n===== EXAMPLE STOP LEVELS FOR PUT OPTIONS =====")
    print(f"Current stock price: ${current_price:.2f}")
    for dte in test_cases:
        buffer = get_dynamic_buffer_for_dte(dte)
        stop_level = current_price * (1 + buffer)
        buffer_pct = buffer * 100
        
        print(f"DTE {dte:3d}: Stop at ${stop_level:.2f} ({buffer_pct:.1f}% above current price)")

if __name__ == "__main__":
    test_dynamic_buffers()