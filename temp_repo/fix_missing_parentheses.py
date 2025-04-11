"""
This script fixes all the missing closing parentheses for the calculate_theta_decay
and calculate_expiry_theta_decay function calls in discord_bot.py
"""

def fix_missing_parentheses():
    """
    Find and fix all instances of missing closing parentheses in calculate_theta_decay
    and calculate_expiry_theta_decay function calls.
    """
    with open('discord_bot.py', 'r') as file:
        lines = file.readlines()
    
    in_calculate_function = False
    function_start_line = 0
    new_lines = []
    
    for i, line in enumerate(lines):
        if ('calculate_theta_decay(' in line or 'calculate_expiry_theta_decay(' in line) and not in_calculate_function:
            in_calculate_function = True
            function_start_line = i
            new_lines.append(line)
        elif in_calculate_function:
            new_lines.append(line)
            
            # Check if this line has the closing parenthesis
            if ')' in line and 'if' not in line and 'try:' not in line and 'except' not in line:
                in_calculate_function = False
            
            # Check if the next line after parameters should have a closing parenthesis
            elif i > function_start_line + 3 and ('hours_ahead=0' in line or 'interval=' in line or 'max_days=' in line) and \
                 (i+1 < len(lines) and ('if' in lines[i+1] or '#' in lines[i+1])):
                # We need to add the closing parenthesis
                new_lines[-1] = new_lines[-1].rstrip() + ')\n'
                in_calculate_function = False
        else:
            new_lines.append(line)
    
    # Write the fixed content back to the file
    with open('discord_bot.py', 'w') as file:
        file.writelines(new_lines)
    
    print("Fixed missing parentheses in all theta decay function calls.")

if __name__ == "__main__":
    fix_missing_parentheses()