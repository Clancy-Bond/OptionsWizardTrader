"""
Fix the contract parts index to use the strike price (index 1) instead of ticker (index 0)
"""

def fix_contract_index():
    print("Fixing contract parts index to use strike price instead of ticker...")
    
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Replace the bullish section
    bullish_replace = content.replace(
        "in-the-money ({contract_parts[0]}.00) options expiring", 
        "in-the-money ({contract_parts[1]}) options expiring"
    )
    
    # Replace the bearish section (apply to the already modified content)
    both_replaced = bullish_replace.replace(
        "in-the-money ({contract_parts[0]}.00) options expiring soon", 
        "in-the-money ({contract_parts[1]}) options expiring soon"
    )
    
    # Write the fixed content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(both_replaced)
    
    print("Contract index fixed! Now using contract_parts[1] for the strike price.")

if __name__ == "__main__":
    fix_contract_index()