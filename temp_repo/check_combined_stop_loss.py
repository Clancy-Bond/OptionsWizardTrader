"""
Test script to check our combined scalp stop loss approach
"""
import yfinance as yf
from combined_scalp_stop_loss import get_combined_scalp_stop_loss

def test_combined_stop_loss():
    """Test the combined stop loss approach for calls and puts"""
    # Test with SPY calls (when VWAP might be above current price)
    spy = yf.Ticker("SPY")
    current_price = spy.info.get('currentPrice', spy.history(period='1d')['Close'].iloc[-1])
    print(f"SPY Current Price: ${current_price:.2f}")
    
    # Test with calls
    print("\nTesting CALL option stop loss:")
    call_result = get_combined_scalp_stop_loss(spy, current_price, "call", days_to_expiration=1)
    print(f"Stop method: {call_result['method']}")
    print(f"Stop level: ${call_result['level']:.2f}")
    print(f"Requires candle close: {call_result['requires_candle_close']}")
    print(f"Recommendation: {call_result['recommendation']}")
    
    # Test with puts
    print("\nTesting PUT option stop loss:")
    put_result = get_combined_scalp_stop_loss(spy, current_price, "put", days_to_expiration=1)
    print(f"Stop method: {put_result['method']}")
    print(f"Stop level: ${put_result['level']:.2f}")
    print(f"Requires candle close: {put_result['requires_candle_close']}")
    print(f"Recommendation: {put_result['recommendation']}")

if __name__ == "__main__":
    test_combined_stop_loss()