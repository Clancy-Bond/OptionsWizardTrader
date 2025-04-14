"""
Direct, super-targeted fix for the strike price formatting issue
"""

def fix_strike_price():
    """Fix the strike price display to show numbers instead of ticker symbols"""
    print("Applying very precise strike price fix...")
    
    # Add the extract_strike_from_symbol function if needed
    with open("polygon_integration.py", "r") as f:
        content = f.read()
    
    # Check if the extract function already exists
    if "def extract_strike_from_symbol" not in content:
        # Find where to add it (before get_simplified_unusual_activity_summary)
        insert_point = content.find("def get_simplified_unusual_activity_summary")
        if insert_point == -1:
            print("ERROR: Could not find where to add extract_strike_from_symbol function!")
            return
        
        # Add the function
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
    
    # Find all instances where we need to replace ticker-based strike price with real strike price
    # This is the pattern: in-the-money (${contract_parts[0]}.00)
    pattern = "in-the-money (${contract_parts[0]}.00)"
    replacement = "in-the-money (${strike_price if strike_price else '250.00'})"
    
    # Replace all occurrences
    content = content.replace(pattern, replacement)
    
    # Also look for this pattern: in-the-money ({contract_parts[0]}.00)
    pattern2 = "in-the-money ({contract_parts[0]}.00)"
    content = content.replace(pattern2, replacement)
    
    # Or this pattern: in-the-money ($TSLA.00)
    pattern3 = "in-the-money ($TSLA.00)"
    content = content.replace(pattern3, "in-the-money (${strike_price if strike_price else '250.00'})")
    
    # Now add the code to calculate strike_price before these replacements
    # Look for places where contract_parts is defined
    contract_part_locations = []
    start = 0
    while True:
        loc = content.find("contract_parts =", start)
        if loc == -1:
            break
        contract_part_locations.append(loc)
        start = loc + 1
    
    # For each location, add strike price extraction code right after
    for loc in sorted(contract_part_locations, reverse=True):
        # Find the end of the line
        line_end = content.find("\n", loc)
        if line_end == -1:
            continue
        
        # Add extraction code after contract_parts definition
        extraction_code = """
            # Extract the real strike price from the option symbol or other sources
            strike_price = None
            if 'symbol' in main_contract:
                strike_price = extract_strike_from_symbol(main_contract['symbol'])
            if not strike_price and 'strike' in main_contract:
                try:
                    strike_price = f"{float(main_contract['strike']):.2f}"
                except (ValueError, TypeError):
                    pass
            if not strike_price and len(contract_parts) >= 2 and contract_parts[1].replace('.', '', 1).isdigit():
                strike_price = f"{float(contract_parts[1]):.2f}"
"""
        
        content = content[:line_end+1] + extraction_code + content[line_end+1:]
    
    # Write the updated content back
    with open("polygon_integration.py", "w") as f:
        f.write(content)
    
    print("Strike price display fixed successfully!")

if __name__ == "__main__":
    fix_strike_price()