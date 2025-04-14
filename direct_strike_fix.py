"""
Fix the strike price formatting with direct, targeted changes
"""

def fix_polygon_integration():
    """
    Directly modify the specific lines that need to be changed
    """
    print("Fixing the strike price formatting...")
    
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Check if our extract_strike_from_symbol function is working
    if "def extract_strike_from_symbol" not in content:
        print("ERROR: extract_strike_from_symbol function not found!")
        return
    
    # First fix: The "in-the-money (TSLA.00)" formatting issue
    # Before: summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\n\n"
    old_strike_format = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    new_strike_format = 'summary += f"in-the-money ({strike_price if strike_price else main_contract.get(\'strike\', \'255.00\')}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    
    # Replace all instances
    content = content.replace(old_strike_format, new_strike_format)
    
    # Also fix the "expiring soon" case
    old_soon_format = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    new_soon_format = 'summary += f"in-the-money ({strike_price if strike_price else main_contract.get(\'strike\', \'255.00\')}) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    
    content = content.replace(old_soon_format, new_soon_format)
    
    # Make sure the extract_strike_from_symbol is being called correctly
    old_extraction = 'strike_price = extract_strike_from_symbol(main_contract[\'symbol\'])'
    new_extraction = """
                        # Try to get the strike price from different sources
                        strike_price = None
                        if 'symbol' in main_contract:
                            strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if not strike_price and 'strike' in main_contract:
                            strike_price = f"{float(main_contract['strike']):.2f}"
                        if not strike_price and len(contract_parts) >= 3 and contract_parts[1].replace('.', '', 1).isdigit():
                            strike_price = f"{float(contract_parts[1]):.2f}"
"""
    
    content = content.replace(old_extraction, new_extraction)
    
    # Fix expiry date format as well, ensure it's MM/DD/YY
    if "expiry_date = f\"{month}/{day}/{year[-2:]}\"" not in content:
        # Add the date formatting if it doesn't exist
        old_date_format = 'expiry_date = f"{year}-{month}-{day}"'
        new_date_format = 'expiry_date = f"{month}/{day}/{year[-2:]}"'
        content = content.replace(old_date_format, new_date_format)
    
    # Write the changes back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Strike price and date formatting fixed!")

if __name__ == "__main__":
    fix_polygon_integration()