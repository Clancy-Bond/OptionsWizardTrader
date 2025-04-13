"""
Exact format fix for unusual options activity output
"""

def fix_exact_format():
    """Apply very specific replacements to fix the exact formatting issues"""
    
    print("Applying exact format fixes...")
    
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # 1. Fix: Remove newline between "million bullish" and "in-the-money"
    content = content.replace('million bullish**\n', 'million bullish** ')
    content = content.replace('million bearish**\n', 'million bearish** ')
    
    # 2. Fix: Replace ${contract_parts[0]} with {contract_parts[0]}.00
    content = content.replace('in-the-money (${contract_parts[0]})', 'in-the-money ({contract_parts[0]}.00)')
    
    # 3. Fix: Ensure date format is MM/DD/YY
    # Update how dates are parsed from option symbols
    content = content.replace(
        'year = \'20\' + ticker_part[date_start:date_start+2]\n        month = ticker_part[date_start+2:date_start+4]\n        day = ticker_part[date_start+4:date_start+6]\n        expiry_date = f"{month}/{day}/{year[-2:]}"',
        'year = \'20\' + ticker_part[date_start:date_start+2]\n        month = ticker_part[date_start+2:date_start+4]\n        day = ticker_part[date_start+4:date_start+6]\n        expiry_date = f"{month}/{day}/{year[-2:]}"  # Already in MM/DD/YY format'
    )
    
    # 4. Fix: Remove "on" before expiration date
    content = content.replace('options expiring on {expiry_date}', 'options expiring {expiry_date}')
    
    # 5. Directly fix the final format string for bullish activity
    bullish_format_old = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    bullish_format_new = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    content = content.replace(bullish_format_old, bullish_format_new)
    
    # 6. Also fix the fallback format string for bullish activity
    bullish_fallback_old = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    bullish_fallback_new = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    content = content.replace(bullish_fallback_old, bullish_fallback_new)
    
    # 7. Fix bearish format string
    bearish_format_old = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    bearish_format_new = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    content = content.replace(bearish_format_old, bearish_format_new)
    
    # 8. Fix bearish fallback format string
    bearish_fallback_old = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    bearish_fallback_new = 'summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    content = content.replace(bearish_fallback_old, bearish_fallback_new)
    
    # Write the fixed content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Exact format fixes applied!")

if __name__ == "__main__":
    fix_exact_format()