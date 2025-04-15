"""
Test the dynamic option moneyness detection for options
"""
from polygon_integration import get_option_moneyness, is_option_in_the_money, get_current_price

def test_option_moneyness():
    """Test option moneyness classification"""
    # Test cases with different combinations of options
    test_cases = [
        # Symbol format: O:TSLA250417C00252500 (Tesla $252.50 call expiring 2025-04-17)
        {"ticker": "TSLA", "symbol": "O:TSLA250417C00252500", "strike": "252.50"},
        # Symbol format: O:AAPL250417P00170000 (Apple $170.00 put expiring 2025-04-17)
        {"ticker": "AAPL", "symbol": "O:AAPL250417P00170000", "strike": "170.00"},
        # Symbol format: O:NVDA250417C00900000 (NVIDIA $900.00 call expiring 2025-04-17)
        {"ticker": "NVDA", "symbol": "O:NVDA250417C00900000", "strike": "900.00"},
        # Symbol format: O:SPY250417P00500000 (SPY $500.00 put expiring 2025-04-17)
        {"ticker": "SPY", "symbol": "O:SPY250417P00500000", "strike": "500.00"}
    ]
    
    # Test each case
    for case in test_cases:
        ticker = case["ticker"]
        symbol = case["symbol"]
        strike = case["strike"]
        
        # Get the current price
        current_price = get_current_price(ticker)
        print(f"\n--- Testing {ticker} ---")
        print(f"Symbol: {symbol}")
        print(f"Strike: {strike}")
        print(f"Current price: {current_price}")
        
        # Determine if it's in-the-money
        is_itm, option_type = is_option_in_the_money(symbol, strike, current_price)
        
        # Get moneyness description (with and without sentiment hint)
        moneyness = get_option_moneyness(symbol, strike, current_price)
        moneyness_bullish = get_option_moneyness(symbol, strike, current_price, "bullish")
        moneyness_bearish = get_option_moneyness(symbol, strike, current_price, "bearish")
        
        print(f"Option type: {option_type}")
        print(f"In-the-money? {is_itm}")
        print(f"Moneyness description: {moneyness}")
        print(f"Moneyness (with bullish hint): {moneyness_bullish}")
        print(f"Moneyness (with bearish hint): {moneyness_bearish}")
        
        # Test with a symbol that might not clearly indicate option type
        unclear_symbol = ticker
        print(f"\nTesting unclear symbol: {unclear_symbol}")
        
        # With no sentiment hint (should default to something)
        moneyness_unclear = get_option_moneyness(unclear_symbol, strike, current_price)
        print(f"Moneyness (no hint): {moneyness_unclear}")
        
        # With sentiment hints
        moneyness_unclear_bullish = get_option_moneyness(unclear_symbol, strike, current_price, "bullish")
        moneyness_unclear_bearish = get_option_moneyness(unclear_symbol, strike, current_price, "bearish")
        print(f"Moneyness (bullish hint): {moneyness_unclear_bullish}")
        print(f"Moneyness (bearish hint): {moneyness_unclear_bearish}")

if __name__ == "__main__":
    print("Testing option moneyness detection...")
    test_option_moneyness()
    print("\nTest completed!")