"""
Test script to check if we can get real transaction dates for options
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from polygon_trades import get_option_trade_data

# Load environment variables
load_dotenv()

# Test Apple option
ticker = "AAPL"
strike = 200
expiry = "2025-04-17"

# Format option symbol
strike_price_padded = f"{strike:08.0f}"
option_date = datetime.strptime(expiry, '%Y-%m-%d')
option_date_str = option_date.strftime('%y%m%d')

# Test both call and put
call_symbol = f"O:{ticker}{option_date_str}C{strike_price_padded}"
put_symbol = f"O:{ticker}{option_date_str}P{strike_price_padded}"

print(f"\nTesting call option: {call_symbol}")
call_data = get_option_trade_data(call_symbol)
if call_data:
    print(f"  ✓ Got call option trade data: {call_data}")
    if 'date' in call_data:
        print(f"  ✓ Transaction date: {call_data['date']}")
else:
    print("  ✗ Could not get call option trade data")

print(f"\nTesting put option: {put_symbol}")
put_data = get_option_trade_data(put_symbol)
if put_data:
    print(f"  ✓ Got put option trade data: {put_data}")
    if 'date' in put_data:
        print(f"  ✓ Transaction date: {put_data['date']}")
else:
    print("  ✗ Could not get put option trade data")

# Try a few more tickers
other_tickers = ["TSLA", "MSFT", "AMZN"]
for ticker in other_tickers:
    # Just do calls
    call_symbol = f"O:{ticker}{option_date_str}C{strike_price_padded}"
    print(f"\nTesting {ticker} call option: {call_symbol}")
    data = get_option_trade_data(call_symbol)
    if data:
        print(f"  ✓ Got trade data: {data}")
    else:
        print("  ✗ Could not get trade data")