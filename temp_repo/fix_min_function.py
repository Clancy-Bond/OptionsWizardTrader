"""
Fix for line 1088-1089 in discord_bot.py
"""

def fix_min_function():
    """Fix the min function issue on line 1088-1089"""
    with open('discord_bot.py', 'r') as f:
        lines = f.readlines()
    
    # Find the line with the min function call
    for i, line in enumerate(lines):
        if 'closest_strike_idx = min(range(len(strike_prices)),' in line and i < len(lines) - 1:
            # Check if the next line contains the key=lambda part
            if 'key=lambda' in lines[i+1]:
                # Combine the two lines
                combined_line = line.rstrip() + ' ' + lines[i+1].strip() + '\n'
                lines[i] = combined_line
                # Remove the next line
                lines[i+1] = ''
                print(f"Fixed min function call at line {i+1}")
    
    # Write the fixed content back to the file
    with open('discord_bot.py', 'w') as f:
        f.writelines(lines)
    
    print("Fixed min function issue in discord_bot.py")

if __name__ == "__main__":
    fix_min_function()