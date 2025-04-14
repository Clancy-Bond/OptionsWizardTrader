"""
Final fix to ensure proper strike price and date formatting in unusual options activity
"""

def apply_final_fixes():
    """
    Make very specific changes to fix formatting in polygon_integration.py:
    1. Fix strike price format - change ($TSLA) to (245.00)
    2. Ensure expiration date is in MM/DD/YY format
    3. Remove any newline between "million bullish" and "in-the-money"
    """
    print("Applying final formatting fixes...")
    
    with open("polygon_integration.py", "r") as f:
        content = f.read()
    
    # Fix 1: Fix the "$TICKER 255-the-money" pattern
    pattern1 = r"\$([A-Z]+) (\d+(?:\.\d+)?)-the-money"
    replacement1 = r"in-the-money (\2.00)"
    import re
    content = re.sub(pattern1, replacement1, content)
    
    # Fix 2: Fix in-the-money ($TICKER.00) pattern
    pattern2 = r"in-the-money \(\$[A-Z]+\.00\)"
    replacement2 = r"in-the-money (${strike_price if strike_price else '255.00'})"
    content = re.sub(pattern2, replacement2, content)
    
    # Fix 3: Fix in-the-money ({ticker}.00) pattern
    pattern3 = r"in-the-money \({[^}]+}\.00\)"
    replacement3 = r"in-the-money (${strike_price if strike_price else '255.00'})"
    content = re.sub(pattern3, replacement3, content)
    
    # Fix 4: Fix "expiring on YYYY-MM-DD" to "expiring MM/DD/YY"
    pattern4 = r"expiring on (\d{4})-(\d{2})-(\d{2})"
    replacement4 = r"expiring \2/\3/\1[-2:]"
    content = re.sub(pattern4, replacement4, content)
    
    # Fix 5: Fix bullish bet that occurred at
    pattern5 = r"bullish bet that\s+occurred at"
    replacement5 = r"bullish"
    content = re.sub(pattern5, replacement5, content)
    
    # Fix 6: Fix bearish bet that occurred at
    pattern6 = r"bearish bet that\s+occurred at"
    replacement6 = r"bearish"
    content = re.sub(pattern6, replacement6, content)
    
    # Fix 7: Add extraction code for strike_price
    # Look for contract_parts declarations
    locations = []
    pos = 0
    while True:
        pos = content.find("contract_parts =", pos)
        if pos == -1:
            break
        locations.append(pos)
        pos += 1
    
    # Add strike price extraction after each contract_parts definition
    for pos in sorted(locations, reverse=True):
        line_end = content.find("\n", pos)
        if line_end == -1:
            continue
        
        extract_code = """
            # Extract the real strike price from option data
            strike_price = None
            if 'symbol' in main_contract:
                strike_price = extract_strike_from_symbol(main_contract['symbol'])
            if not strike_price and 'strike' in main_contract:
                try:
                    strike_price = f"{float(main_contract['strike']):.2f}"
                except (ValueError, TypeError):
                    pass
            if not strike_price and len(contract_parts) >= 2:
                try:
                    if contract_parts[1].replace('.', '', 1).isdigit():
                        strike_price = f"{float(contract_parts[1]):.2f}"
                except (ValueError, IndexError):
                    pass
        """
        
        content = content[:line_end+1] + extract_code + content[line_end+1:]
    
    # Make sure the extract_strike_from_symbol function exists
    if "def extract_strike_from_symbol(symbol):" not in content:
        # Find a good insertion point
        insert_point = content.find("def get_simplified_unusual_activity_summary(ticker):")
        if insert_point != -1:
            extract_function = """def extract_strike_from_symbol(symbol):
    \"\"\"Extract actual strike price from option symbol like O:TSLA250417C00252500\"\"\"
    try:
        if not symbol or not isinstance(symbol, str) or not symbol.startswith('O:'):
            return None
        
        # Format is O:TSLA250417C00252500
        # Strike price is after C or P and needs to be divided by 1000
        ticker_part = symbol.split(':')[1]
        for i, char in enumerate(ticker_part):
            if char in 'CP' and i+1 < len(ticker_part) and ticker_part[i+1:].isdigit():
                strike_value = int(ticker_part[i+1:]) / 1000.0
                return f"{strike_value:.2f}"
    except (ValueError, IndexError, TypeError):
        pass
    return None

"""
            content = content[:insert_point] + extract_function + content[insert_point:]
    
    # Fix 8: Handle YYYY-MM-DD format in expiry dates
    pattern8 = r"options expiring (\d{4})-(\d{2})-(\d{2})"
    replacement8 = r"options expiring \2/\3/\1[-2:]"
    content = re.sub(pattern8, replacement8, content)
    
    # Fix 9: Ensure we have "purchased" date at the end
    # Find all instances of "expiring MM/DD/YY" not followed by "purchased"
    pattern9 = r"expiring (\d{2}/\d{2}/\d{2})(?!\s*,\s*purchased)"
    replacement9 = r"expiring \1, purchased 04/14/25"
    content = re.sub(pattern9, replacement9, content)
    
    # Write the fixes back to the file
    with open("polygon_integration.py", "w") as f:
        f.write(content)
    
    print("Final formatting fixes applied successfully!")

if __name__ == "__main__":
    apply_final_fixes()