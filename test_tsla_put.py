"""
Check details of the TSLA 260 April 25, 2025 PUT trade
"""
import os
import requests
from polygon_trades import get_option_trade_data, format_timestamp

def examine_option_trades(option_symbol):
    """
    Get detailed information about trades for a specific option
    """
    print(f"\n===== EXAMINING TRADES FOR: {option_symbol} =====\n")
    
    # Get the trade data
    trade_data = get_option_trade_data(option_symbol)
    
    if not trade_data:
        print("No trade data found for this option")
        return
    
    print("Trade data:")
    for key, value in trade_data.items():
        print(f"  {key}: {value}")
    
    if 'timestamp_human' in trade_data:
        formatted_time = trade_data['timestamp_human']
        print(f"\nHuman-readable timestamp: {formatted_time}")
        
        # Verify format
        timestamp_parts = formatted_time.split()
        if len(timestamp_parts) >= 3:
            date_part = timestamp_parts[0]
            time_part = " ".join(timestamp_parts[1:3])
            timezone_part = timestamp_parts[3] if len(timestamp_parts) > 3 else ""
            
            print(f"Date part: {date_part}")
            print(f"Time part: {time_part}")
            print(f"Timezone: {timezone_part}")
            
            # Check if it matches our desired format (MM/DD/YY HH:MM:SS AM/PM ET)
            if '/' in date_part and ('AM' in time_part or 'PM' in time_part) and 'ET' in timezone_part:
                print("\n✅ TIMESTAMP FORMAT CORRECT")
            else:
                print("\n❌ TIMESTAMP FORMAT INCORRECT")
    else:
        print("\nNo timestamp information available")
        
    # Check if trade size is large enough to be considered unusual
    if 'size' in trade_data:
        size = trade_data['size']
        if size >= 50:
            print(f"This is a large block trade (size: {size})")
        elif size >= 10:
            print(f"This is a medium-sized trade (size: {size})")
        else:
            print(f"This is a standard-sized trade (size: {size})")
            
if __name__ == "__main__":
    # Test with a known TSLA put option
    examine_option_trades("O:TSLA250425P00260000")