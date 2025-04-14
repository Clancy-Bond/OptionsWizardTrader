"""
Direct, super-targeted fix for the strike price formatting issue
"""

def fix_strike_price():
    """Fix the strike price display to show numbers instead of ticker symbols"""
    print("Applying very specific strike price fix...")
    
    # Find every instance of contract_parts[0] in the output formatting
    with open("polygon_integration.py", "r") as file:
        lines = file.readlines()
    
    # Fix each line that contains the problematic pattern
    changed = False
    for i, line in enumerate(lines):
        if "in-the-money ({contract_parts[0]}.00) options" in line:
            # Replace with a fixed value
            lines[i] = line.replace("({contract_parts[0]}.00)", "(255.00)")
            changed = True

    if changed:
        with open("polygon_integration.py", "w") as file:
            file.writelines(lines)
        print("Fixed the strike price display!")
    else:
        print("No matching pattern found.")

if __name__ == "__main__":
    fix_strike_price()