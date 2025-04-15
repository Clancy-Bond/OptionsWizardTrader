"""
Exact format fix for unusual options activity output
"""

def fix_exact_format():
    """Apply very specific replacements to fix the exact formatting issues"""
    
    # Read current file content
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Create backup
    with open('polygon_integration.py.bak2', 'w') as file:
        file.write(content)
    
    # First, add the determine_moneyness function after the extract_strike_from_symbol function
    if "def determine_moneyness(" not in content:
        moneyness_function = """
def determine_moneyness(strike_price, stock_price, option_type):
    """
    Determine if an option is in-the-money or out-of-the-money
    
    Args:
        strike_price: Option strike price (as float or string)
        stock_price: Current stock price
        option_type: 'call' or 'put'
        
    Returns:
        String: 'in-the-money' or 'out-of-the-money'
    """
    try:
        # Convert strike price to float if it's a string
        if isinstance(strike_price, str):
            strike_price = float(strike_price)
            
        # For call options: in-the-money if strike < stock price
        if option_type.lower() == 'call':
            return 'in-the-money' if strike_price < stock_price else 'out-of-the-money'
        # For put options: in-the-money if strike > stock price
        elif option_type.lower() == 'put':
            return 'in-the-money' if strike_price > stock_price else 'out-of-the-money'
        else:
            return 'in-the-money'  # Default to in-the-money if we can't determine
    except (ValueError, TypeError):
        return 'in-the-money'  # Default to in-the-money if conversion fails
"""
        
        # Find position after extract_strike_from_symbol
        insert_pos = content.find("def get_simplified_unusual_activity_summary(")
        if insert_pos > 0:
            content = content[:insert_pos] + moneyness_function + "\n\n" + content[insert_pos:]
    
    # Add current_stock_price to the metadata if not present
    if "'current_stock_price': stock_price" not in content:
        content = content.replace(
            "'all_options_analyzed': len(all_options)",
            "'all_options_analyzed': len(all_options),\n            'current_stock_price': stock_price"
        )
    
    # Apply fixes by exact replacements - for bullish options section
    content = content.replace(
        'summary += f"in-the-money ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.',
        'summary += f"in-the-money ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}."'
    )
    
    content = content.replace(
        'summary += f"in-the-money ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.',
        'summary += f"in-the-money ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}."'
    )
    
    content = content.replace(
        'summary += f"in-the-money ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.',
        'summary += f"in-the-money ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}."'
    )
    
    # Apply fixes for bearish options section (same patterns)
    content = content.replace(
        'summary += f"in-the-money ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.',
        'summary += f"in-the-money ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}."'
    )
    
    content = content.replace(
        'summary += f"in-the-money ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.',
        'summary += f"in-the-money ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}."'
    )
    
    content = content.replace(
        'summary += f"in-the-money ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.',
        'summary += f"in-the-money ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}."'
    )
    
    # Write updated content
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Format fixes applied successfully!")

if __name__ == "__main__":
    fix_exact_format()