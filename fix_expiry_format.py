"""
Fix the expiration date format to ensure consistent MM/DD/YY format
"""

def fix_expiry_date_format():
    """
    Make specific changes to fix the expiration date format in polygon_integration.py
    to ensure it's consistently in MM/DD/YY format with no leading "on"
    """
    
    print("Fixing expiration date format...")
    
    # Read the current file
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Original parsing logic is good at line 1028: expiry_date = f"{month}/{day}/{year[-2:]}"
    # But we need to fix where it's used in the output string
    
    # Fix expiry date display formatting - remove "on" and ensure proper format
    content = content.replace(
        'options expiring on {expiry_date},',
        'options expiring {expiry_date},'
    )
    
    # Write the updated content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Expiration date format fixed successfully!")

if __name__ == "__main__":
    fix_expiry_date_format()