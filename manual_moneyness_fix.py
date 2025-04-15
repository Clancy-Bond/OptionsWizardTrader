"""
This script will manually implement the moneyness fix by completely 
rebuilding the relevant sections with proper syntax.
"""

from fixed_moneyness import determine_moneyness

# First, we'll restore the original file without the broken syntax
with open('moneyness_patch.diff', 'r') as file:
    content = file.read()

# Extract the determine_moneyness function
with open('fixed_moneyness.py', 'r') as file:
    moneyness_function = file.read()

# Read in the current corrupted file
with open('polygon_integration.py', 'r') as file:
    current_content = file.read()

# Create a backup
with open('polygon_integration.py.bak', 'w') as file:
    file.write(current_content)

# Replace corrupted "determine_moneyness" function 
print("Implementing moneyness fix...")

# Define a simplified replacement pattern
def replace_moneyness(options_type, content):
    """Replace in-the-money with proper moneyness determination for a specific option type"""
    # For strike price with symbol
    old_pattern = f'strike_price = extract_strike_from_symbol(main_contract[\'symbol\'])\n        if strike_price:\n            summary += f"in-the-money ({{strike_price}}) options expiring {{expiry_date}}, purchased {{timestamp_str if timestamp_str else \'2025-04-14\'}}.'
    new_pattern = f'''strike_price = extract_strike_from_symbol(main_contract['symbol'])
        if strike_price:
            # Determine if {options_type} option is in-the-money based on strike and stock price
            stock_price = result_with_metadata.get('current_stock_price', 0)
            moneyness = determine_moneyness(strike_price, stock_price, '{options_type}')
            summary += f"{{moneyness}} ({{strike_price}}) options expiring {{expiry_date}}, purchased {{timestamp_str if timestamp_str else '2025-04-14'}}.\n\n"'''
    
    content = content.replace(old_pattern, new_pattern)
    
    # For contract_parts version
    old_pattern = f'summary += f"in-the-money ({{contract_parts[1]}}) options expiring {{expiry_date}}, purchased {{timestamp_str if timestamp_str else \'2025-04-14\'}}.'
    new_pattern = f'''# Check moneyness for contract parts
            try:
                strike_from_parts = float(contract_parts[1])
                moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get('current_stock_price', 0), '{options_type}')
            except (ValueError, IndexError):
                moneyness = "in-the-money"  # Default if we can't determine
            summary += f"{{moneyness}} ({{contract_parts[1]}}) options expiring {{expiry_date}}, purchased {{timestamp_str if timestamp_str else '2025-04-14'}}.\n\n"'''
    
    content = content.replace(old_pattern, new_pattern)
    
    # For options expiring soon
    old_pattern = f'summary += f"in-the-money ({{contract_parts[1]}}) options expiring soon, purchased {{timestamp_str if timestamp_str else \'2025-04-14\'}}.'
    new_pattern = f'''# Check moneyness for soon-expiring options
                try:
                    strike_from_parts = float(contract_parts[1])
                    moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get('current_stock_price', 0), '{options_type}')
                except (ValueError, IndexError):
                    moneyness = "in-the-money"  # Default if we can't determine
                summary += f"{{moneyness}} ({{contract_parts[1]}}) options expiring soon, purchased {{timestamp_str if timestamp_str else '2025-04-14'}}.\n\n"'''
    
    content = content.replace(old_pattern, new_pattern)
    
    return content

# Replace the original file with the fixed version
with open('polygon_integration.py', 'r') as file:
    content = file.read()

# Insert determine_moneyness function if it doesn't exist already
if "def determine_moneyness(" not in content:
    # Find the position after extract_strike_from_symbol function
    insert_pos = content.find("def extract_strike_from_symbol(") 
    if insert_pos > 0:
        # Find the end of that function
        func_end = content.find("def ", insert_pos + 10)
        if func_end > 0:
            # Insert our function after it
            content = content[:func_end] + "\n" + determine_moneyness.__doc__ + "\n" + content[func_end:]

# Apply the moneyness determination logic for calls and puts
content = replace_moneyness('call', content)
content = replace_moneyness('put', content)

# Ensure current_stock_price is included in the metadata
if "'current_stock_price': stock_price" not in content:
    pattern = "'all_options_analyzed': len(all_options)"
    replacement = "'all_options_analyzed': len(all_options),\n            'current_stock_price': stock_price"
    content = content.replace(pattern, replacement)

# Write the fixed content
with open('polygon_integration.py', 'w') as file:
    file.write(content)

print("Moneyness fix applied successfully. Backup saved as polygon_integration.py.bak")