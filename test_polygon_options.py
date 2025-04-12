"""
Test script to verify we're only getting option strikes from Polygon.io
and not mixing data sources.
"""
import os
import dotenv
from datetime import datetime
import polygon_integration as polygon

# Load environment variables
dotenv.load_dotenv()

def main():
    # Check if Polygon API key is available
    if not os.getenv("POLYGON_API_KEY"):
        print("ERROR: POLYGON_API_KEY environment variable not set")
        return
    
    # Test tickers
    test_tickers = ["SPY", "AAPL", "TSLA"]
    
    for ticker in test_tickers:
        print(f"\n=== Testing {ticker} options data ===")
        
        # 1. Get option expirations
        print(f"1. Getting available expiration dates for {ticker}...")
        expirations = polygon.get_option_expirations(ticker)
        
        if not expirations:
            print(f"No expiration dates found for {ticker}")
            continue
            
        # Use the first expiration
        exp_date = expirations[0]
        print(f"Using expiration date: {exp_date}")
        
        # 2. Get option chain
        print(f"2. Getting option chain for {ticker} at {exp_date}...")
        option_chain = polygon.get_option_chain(ticker, exp_date)
        
        if not option_chain:
            print(f"No option chain data found for {ticker} at {exp_date}")
            continue
            
        # 3. List the call strike prices
        if "calls" in option_chain and option_chain["calls"]:
            print(f"3. Call option strikes for {ticker} at {exp_date}:")
            call_strikes = sorted([float(option["strike_price"]) for option in option_chain["calls"]])
            print(f"   Range: {min(call_strikes)} to {max(call_strikes)}")
            print(f"   Total strikes: {len(call_strikes)}")
            
            # Print some sample strikes
            sample_count = min(5, len(call_strikes))
            sample_strikes = call_strikes[:sample_count]
            print(f"   Sample strikes: {sample_strikes}")
        else:
            print(f"No call options found for {ticker} at {exp_date}")
        
        # 4. Try to get unusual activity
        print(f"4. Checking for unusual options activity for {ticker}...")
        unusual_activity = polygon.get_unusual_options_activity(ticker)
        
        if unusual_activity:
            print(f"   Found {len(unusual_activity)} unusual activity items")
            
            # Print sample of unusual activity
            for i, activity in enumerate(unusual_activity[:2]):  # Show max 2 samples
                print(f"   Activity {i+1}: {activity['contract']}")
                if 'transaction_date' in activity:
                    print(f"     Transaction date: {activity['transaction_date']}")
                print(f"     Volume: {activity['volume']}, Premium: ${activity['premium']:,.0f}")
        else:
            print(f"   No unusual options activity found for {ticker}")

if __name__ == "__main__":
    main()