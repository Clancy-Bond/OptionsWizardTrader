import yfinance as yf
import datetime

ticker = yf.Ticker('TSLA')
current_price = ticker.info.get('currentPrice')
if current_price is None:
    current_price = ticker.history(period='1d')['Close'].iloc[-1]

print(f'Current TSLA price: ${current_price:.2f}')
print(f'Last updated data timestamp: {ticker.history(period="1d").index[-1]}')

# Also check the option chain to verify the $400 puts
try:
    expirations = ticker.options
    print(f"\nAvailable expiration dates: {expirations[:3]}...")
    
    # Check April 17, 2025 options if available
    target_date = None
    for date in expirations:
        if '2025-04-17' in date:
            target_date = date
            break
    
    if target_date:
        print(f"\nChecking options for {target_date}")
        options = ticker.option_chain(target_date)
        
        # Find $400 strike puts
        for idx, put in options.puts[options.puts['strike'] == 400].iterrows():
            print(f"$400 put details:")
            print(f"  Volume: {put['volume']}")
            print(f"  Open Interest: {put['openInterest']}")
            print(f"  Last Price: ${put['lastPrice']:.2f}")
            print(f"  In-the-money: {put['inTheMoney']}")
            break
    else:
        print("Could not find April 17, 2025 expiration date")
except Exception as e:
    print(f"Error checking options: {e}")
