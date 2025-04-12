"""
Test the flow generation with a single predefined option
"""
from polygon_trades import get_option_trade_data, format_timestamp
import sys

def format_mock_activity(option_symbol, sentiment="bullish"):
    """
    Create a mock activity entry for one option to test our formatting
    """
    print(f"\n===== TESTING FORMAT FOR: {option_symbol} =====\n")
    
    # Get the actual trade data from Polygon API
    trade_data = get_option_trade_data(option_symbol)
    
    if not trade_data:
        print("No trade data found!")
        return
    
    # Basic formatting
    ticker = option_symbol.split(':')[1][:4] if ':' in option_symbol else "AAPL"
    strike = "200"
    expiry = "04/25/25"
    premium = 1500000  # $1.5M
    
    # Format expiration date from option symbol if possible
    if option_symbol.startswith('O:'):
        ticker_part = option_symbol.split(':')[1]
        date_start = len(ticker_part.split()[0])
        if len(ticker_part) > date_start + 6:
            year = '20' + ticker_part[date_start:date_start+2]
            month = ticker_part[date_start+2:date_start+4]
            day = ticker_part[date_start+4:date_start+6]
            expiry = f"{month}/{day}/{year[-2:]}"
    
    # Get the timestamp
    timestamp_str = ""
    if 'timestamp_human' in trade_data:
        timestamp_str = trade_data['timestamp_human']
    
    # Create a formatted summary
    summary = f"🐳 {ticker} Unusual Activity Test 🐳\n\n"
    summary += f"• Unusual activity score: 45/100 (based on large block trades and premium size)\n\n"
    
    if sentiment == "bullish":
        # Format with timestamp
        if timestamp_str:
            summary += f"• I'm seeing bullish activity for {ticker}. The largest flow is a $1.5 million bullish bet\n"
            summary += f"occurred at {timestamp_str} with "
        else:
            summary += f"• I'm seeing bullish activity for {ticker}. The largest flow is a $1.5 million bullish\n"
            summary += f"bet with "
        
        summary += f"in-the-money (${strike}) options expiring on {expiry}.\n\n"
    else:
        # Format with timestamp
        if timestamp_str:
            summary += f"• I'm seeing bearish activity for {ticker}. The largest flow is a $1.5 million bearish bet\n"
            summary += f"occurred at {timestamp_str} with "
        else:
            summary += f"• I'm seeing bearish activity for {ticker}. The largest flow is a $1.5 million bearish\n"
            summary += f"bet with "
        
        summary += f"in-the-money (${strike}) options expiring on {expiry}.\n\n"
    
    # Add overall flow
    summary += f"Overall flow: 75% bullish / 25% bearish"
    
    print("\n===== FORMATTED OUTPUT =====\n")
    print(summary)
    
    # Verification
    if timestamp_str and "occurred at" in summary:
        print("\n✅ TIMESTAMP PROPERLY INTEGRATED")
    else:
        print("\n❌ TIMESTAMP MISSING OR IMPROPERLY FORMATTED")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        option_symbol = sys.argv[1]
    else:
        option_symbol = "O:TSLA250425P00260000"  # Default test option
    
    format_mock_activity(option_symbol)