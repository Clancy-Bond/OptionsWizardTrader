"""
Direct test for the new unusual options activity scoring system
Bypasses Discord bot to test directly
"""

import polygon_integration

def test_unusual_activity(ticker):
    """
    Test the unusual options activity detection directly
    """
    # Get the simplified summary
    result = polygon_integration.get_simplified_unusual_activity_summary(ticker)
    
    print(result)
    
    # Print specific important checks for our formatting
    lines = result.split("\n")
    for line in lines:
        if "million bullish" in line or "million bearish" in line:
            print("\nFound the flow line:")
            print(line)
            
        if "in-the-money" in line:
            in_money_parts = line.split("in-the-money")
            if len(in_money_parts) > 1:
                print("\nStrike price format:")
                print(in_money_parts[1].strip())
                
        if "expiring" in line:
            expiry_parts = line.split("expiring")
            if len(expiry_parts) > 1:
                print("\nExpiry date format:")
                print(expiry_parts[1].strip())
                
        if "purchased" in line:
            purchase_parts = line.split("purchased")
            if len(purchase_parts) > 1:
                print("\nPurchase date format:")
                print(purchase_parts[1].strip())

if __name__ == "__main__":
    print("Testing TSLA unusual activity formatting...")
    test_unusual_activity("TSLA")