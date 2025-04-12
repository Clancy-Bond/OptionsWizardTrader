"""
Check details of the TSLA 260 April 25, 2025 PUT trade
"""
import json
from polygon_trades import get_option_trade_data

def examine_option_trades(option_symbol):
    """
    Get detailed information about trades for a specific option
    """
    print(f"\n===== Examining detailed trades for {option_symbol} =====\n")
    
    # Get trade data
    trade_data = get_option_trade_data(option_symbol)
    
    if not trade_data:
        print("No trade data found")
        return
    
    print("Trade Data:")
    for key, value in trade_data.items():
        print(f"  {key}: {value}")
    
    # Check if the timestamp is in AM/PM format with ET timezone
    if 'timestamp_human' in trade_data:
        timestamp = trade_data['timestamp_human']
        print(f"\nTimestamp Format Check: {timestamp}")
        
        # Verify format
        if 'AM ET' in timestamp or 'PM ET' in timestamp:
            print("✅ Timestamp is in AM/PM format with ET timezone")
        else:
            print("❌ Timestamp does not use AM/PM format with ET timezone")

if __name__ == "__main__":
    # Use the TSLA PUT option with the highest unusualness score
    examine_option_trades("O:TSLA250425P00260000")