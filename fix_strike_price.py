"""
Fix the strike price format
"""

def fix_strike_price():
    """Fix the strike price format to show the actual price value without $"""
    
    print("Fixing strike price format...")
    
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Fix all instances where we have in-the-money (${contract_parts[0]})
    # Change to in-the-money ({contract_parts[0]}.00)
    content = content.replace(
        'in-the-money (${contract_parts[0]})',
        'in-the-money ({contract_parts[0]}.00)'
    )
    
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Strike price format fixed!")

if __name__ == "__main__":
    fix_strike_price()