"""
Test the Discord bot's unusual options activity formatting
This directly tests the output that would be sent to Discord
"""

import polygon_integration
import re

def test_discord_unusual():
    """
    Test the Discord bot's unusual options activity output formatting
    to ensure strike prices are correctly shown as numbers and date formats are correct
    """
    print("Testing TSLA unusual options activity output formatting:")
    print("-" * 60)
    
    # Get the summary
    summary = polygon_integration.get_simplified_unusual_activity_summary("TSLA")
    
    # Print the formatted output
    print(summary)
    print("-" * 60)
    
    # Verify the strike price format
    strike_pattern = r'in-the-money \((\d+\.\d+)\)'
    strike_matches = re.findall(strike_pattern, summary)
    
    if strike_matches:
        print(f"✅ Found proper strike price format: {strike_matches}")
    else:
        print("❌ Could not find proper 'in-the-money (NUMBER)' format")
        
        # Check for problematic formats
        if "$TSLA" in summary:
            print("❌ Found problematic ticker reference: $TSLA")
        
        if "-the-money" in summary:
            print("❌ Found problematic format: X-the-money")
    
    # Verify the expiration date format
    expiry_pattern = r'expiring (\d{2}/\d{2}/\d{2})'
    expiry_matches = re.findall(expiry_pattern, summary)
    
    if expiry_matches:
        print(f"✅ Found proper MM/DD/YY expiration format: {expiry_matches}")
    else:
        print("❌ Could not find proper expiration date format")
        
        # Check for problematic formats
        if "expiring on" in summary:
            print("❌ Found problematic 'expiring on' format")
            
        if "-" in summary and re.search(r'\d{4}-\d{2}-\d{2}', summary):
            print("❌ Found problematic YYYY-MM-DD date format")
    
    # Verify purchase date
    purchase_pattern = r'purchased (\d{2}/\d{2}/\d{2})'
    purchase_matches = re.findall(purchase_pattern, summary)
    
    if purchase_matches:
        print(f"✅ Found proper purchase date format: {purchase_matches}")
    else:
        print("❌ Could not find purchase date")
    
    # Verify no "bet that occurred at" text
    if "bet that" in summary or "occurred at" in summary:
        print("❌ Found problematic 'bet that occurred at' text")
    else:
        print("✅ No problematic 'bet that occurred at' text")

if __name__ == "__main__":
    test_discord_unusual()