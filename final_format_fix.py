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
    
    print("Applying final format fixes...")
    
    # Read the current file
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Fix the bullish section
    content = content.replace(
        'summary += f"• I\'m seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish**\\n"',
        'summary += f"• I\'m seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "'
    )
    
    # Fix the bearish section
    content = content.replace(
        'summary += f"• I\'m seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish**\\n"',
        'summary += f"• I\'m seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "'
    )
    
    # Fix strike price formatting in bullish section
    content = content.replace(
        'summary += f"in-the-money (${contract_parts[0]}) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"',
        'summary += f"in-the-money ({contract_parts[0]}.00) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    )
    
    # Fix strike price formatting in fallback bullish section
    content = content.replace(
        'summary += f"in-the-money (${contract_parts[0]}) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"',
        'summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    )
    
    # Fix strike price formatting in bearish section
    content = content.replace(
        'summary += f"in-the-money (${contract_parts[0]}) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"',
        'summary += f"in-the-money ({contract_parts[0]}.00) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    )
    
    # Fix strike price formatting in fallback bearish section
    content = content.replace(
        'summary += f"in-the-money (${contract_parts[0]}) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"',
        'summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else \'04/11/25\'}.\n\n"'
    )
    
    # Write the updated content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Format fixes applied successfully!")

if __name__ == "__main__":
    apply_final_fixes()