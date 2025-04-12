"""
Quick test for unusual options activity function
"""

from polygon_integration import get_unusual_options_activity
from polygon_integration import get_current_price, get_option_chain

def test_quick(ticker):
    """Quickly test if we can get unusual options activity"""
    print(f"\n=== TESTING UNUSUAL ACTIVITY FOR {ticker} ===\n")
    
    # First check stock price
    price = get_current_price(ticker)
    print(f"{ticker} current price: {price}")
    
    # Check how many options we're getting now
    chain = get_option_chain(ticker)
    if chain:
        print(f"Options chain contains {len(chain)} options")
        
        # Count near the money options
        near_money = sum(1 for option in chain 
                        if 'strike_price' in option 
                        and price 
                        and abs(option['strike_price'] - price) / price <= 0.1)
        print(f"Options near the money (within 10%): {near_money}")
    else:
        print("No options chain data available")
    
    # Get unusual activity
    print("\nChecking for unusual options activity...")
    activity = get_unusual_options_activity(ticker)
    
    if activity:
        print(f"Found {len(activity)} unusual activity items:")
        for i, item in enumerate(activity):
            print(f"\n{i+1}. {item.get('contract', 'Unknown contract')}")
            print(f"   Volume: {item.get('volume', 0)} contracts")
            print(f"   Premium: ${item.get('premium', 0):,.2f}")
            print(f"   Sentiment: {item.get('sentiment', 'neutral')}")
            if 'transaction_date' in item:
                print(f"   Transaction date: {item['transaction_date']}")
    else:
        print("No unusual activity found")

if __name__ == "__main__":
    ticker = input("Enter ticker to test (e.g., AAPL): ").strip().upper()
    test_quick(ticker)