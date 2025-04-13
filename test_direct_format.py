"""
Direct test of the formatting without making API calls
"""

def test_format():
    """Test the formatting directly by examining the structure of the code"""
    
    print("Checking polygon_integration.py for proper formatting...")
    
    with open('polygon_integration.py', 'r') as file:
        content = file.readlines()
    
    # Check for specific formatting patterns
    bullish_format = False
    bearish_format = False
    strike_price_format = False
    expiry_date_format = False
    purchase_date_format = False
    
    for i, line in enumerate(content):
        # Check for bullish format without newline
        if "million bullish**" in line and "\\n" not in line:
            bullish_format = True
            print(f"✅ Line {i+1}: Bullish format correct")
        
        # Check for bearish format without newline
        if "million bearish**" in line and "\\n" not in line:
            bearish_format = True
            print(f"✅ Line {i+1}: Bearish format correct")
        
        # Check for strike price format with .00
        if "in-the-money ({contract_parts[0]}.00)" in line:
            strike_price_format = True
            print(f"✅ Line {i+1}: Strike price format correct")
        
        # Check for expiry date format without "on"
        if "options expiring {expiry_date}" in line and "on {expiry_date}" not in line:
            expiry_date_format = True
            print(f"✅ Line {i+1}: Expiry date format correct")
        
        # Check for purchase date
        if "purchased {timestamp_str" in line:
            purchase_date_format = True
            print(f"✅ Line {i+1}: Purchase date format correct")
    
    # Summary
    print("\nFormatting Status Summary:")
    print("-" * 30)
    print(f"Bullish format: {'✅ CORRECT' if bullish_format else '❌ NEEDS FIX'}")
    print(f"Bearish format: {'✅ CORRECT' if bearish_format else '❌ NEEDS FIX'}")
    print(f"Strike price format: {'✅ CORRECT' if strike_price_format else '❌ NEEDS FIX'}")
    print(f"Expiry date format: {'✅ CORRECT' if expiry_date_format else '❌ NEEDS FIX'}")
    print(f"Purchase date format: {'✅ CORRECT' if purchase_date_format else '❌ NEEDS FIX'}")

if __name__ == "__main__":
    test_format()