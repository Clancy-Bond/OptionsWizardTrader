#!/usr/bin/env python3
"""
Step 1: Fix the in-the-money format
"""

def fix_format_step1():
    """Apply specific change to fix in-the-money format"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Replace bullish section format
    old_format_bullish = 'summary += f"{contract_parts[1]}-the-money (${contract_parts[0]}) options expiring on {expiry_date}.'
    new_format_bullish = 'summary += f"in-the-money (${contract_parts[0]}) options expiring on {expiry_date}.'
    
    content = content.replace(old_format_bullish, new_format_bullish)
    
    # Replace bullish "expiring soon" format 
    old_format_soon_bullish = 'summary += f"{contract_parts[1]}-the-money (${contract_parts[0]}) options expiring soon.'
    new_format_soon_bullish = 'summary += f"in-the-money (${contract_parts[0]}) options expiring soon.'
    
    content = content.replace(old_format_soon_bullish, new_format_soon_bullish)
    
    # Save the changes
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Step 1 complete: Fixed in-the-money format")

if __name__ == "__main__":
    fix_format_step1()