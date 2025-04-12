"""
Test the timestamp and format for a specific option
This focused test helps us verify our timestamp formatting without processing the entire chain
"""
import sys
from polygon_trades import get_option_trade_data, format_timestamp
from datetime import datetime
import pytz

def test_specific_option(option_symbol):
    """
    Test timestamp formatting for a specific option
    
    Args:
        option_symbol: Option symbol in Polygon format (e.g., O:AAPL250417C00195000)
    """
    print(f"\n===== TESTING TIMESTAMP FORMAT FOR: {option_symbol} =====\n")
    
    # Get trade data for this specific option
    try:
        trade_data = get_option_trade_data(option_symbol)
        
        if trade_data:
            print(f"Trade data found:")
            for key, value in trade_data.items():
                print(f"  {key}: {value}")
                
            # Focus on timestamp formatting
            if 'timestamp_human' in trade_data:
                print(f"\nFormatted timestamp: {trade_data['timestamp_human']}")
                
                # Analyze the format
                timestamp_parts = trade_data['timestamp_human'].split()
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
                        print("Expected format: MM/DD/YY HH:MM:SS AM/PM ET")
        else:
            print("No trade data found for this option.")
    except Exception as e:
        print(f"Error testing option: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        option_symbol = sys.argv[1]
    else:
        option_symbol = "O:AAPL250417C00195000"  # Default test option
    
    test_specific_option(option_symbol)