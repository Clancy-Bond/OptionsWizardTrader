"""
Test script to verify the dynamic moneyness calculation
"""
from polygon_integration import get_option_moneyness, is_option_in_the_money, get_current_price, extract_strike_from_symbol

def test_specific_options():
    # Test cases for various options with different strike/current price combinations
    test_cases = [
        {"ticker": "SPY", "symbol": "O:SPY250417C00500000", "strike": "500.00"},  # Call with strike < current for SPY
        {"ticker": "SPY", "symbol": "O:SPY250417P00550000", "strike": "550.00"},  # Put with strike > current for SPY
        {"ticker": "AAPL", "symbol": "O:AAPL250417C00220000", "strike": "220.00"}, # Call with strike > current for AAPL
        {"ticker": "AAPL", "symbol": "O:AAPL250417P00170000", "strike": "170.00"}, # Put with strike < current for AAPL
    ]
    
    print("Testing dynamic moneyness detection...")
    
    for case in test_cases:
        ticker = case["ticker"]
        symbol = case["symbol"]
        strike = case["strike"]
        
        current_price = get_current_price(ticker)
        
        # Extract option type (call/put) from symbol
        is_itm, option_type = is_option_in_the_money(symbol, strike, current_price)
        moneyness = get_option_moneyness(symbol, strike, current_price)
        
        print(f"\n{ticker} - {symbol}")
        print(f"Current price: ${current_price:.2f}")
        print(f"Strike price: ${float(strike):.2f}")
        print(f"Option type: {option_type.upper()}")
        print(f"In the money? {is_itm}")
        print(f"Moneyness: {moneyness}")
        
        # Extra: Test with bullish and bearish hints
        moneyness_bullish = get_option_moneyness(symbol, strike, current_price, "bullish")
        moneyness_bearish = get_option_moneyness(symbol, strike, current_price, "bearish")
        print(f"Moneyness (bullish hint): {moneyness_bullish}")
        print(f"Moneyness (bearish hint): {moneyness_bearish}")

if __name__ == "__main__":
    test_specific_options()