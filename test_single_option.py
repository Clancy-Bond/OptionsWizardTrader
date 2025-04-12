"""
Test enhanced timestamp features on a single option contract
"""
from polygon_trades import get_option_trade_data, format_timestamp

def test_option_timestamps(option_symbol):
    """
    Test the enhanced timestamp functionality for a specific option
    """
    print(f"\nTesting timestamp data for {option_symbol}\n")
    
    # Get trade data with enhanced timestamp information
    trade_data = get_option_trade_data(option_symbol)
    
    if not trade_data:
        print("No trade data found")
        return
    
    print("Trade Data:")
    for key, value in trade_data.items():
        print(f"  {key}: {value}")
    
    # Show that format_timestamp works properly
    if 'timestamp' in trade_data:
        formatted_time = format_timestamp(trade_data['timestamp'])
        print(f"\nFormatted timestamp: {formatted_time}")

if __name__ == "__main__":
    # Test with the TSLA option that had the highest score
    test_option_timestamps("O:TSLA250425P00260000")