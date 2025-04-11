"""
Fix duplicated buffer percentage calculation code in discord_bot.py
"""

def fix_duplicated_buffer_code():
    """Remove the duplicated buffer calculation code"""
    
    with open('discord_bot.py', 'r') as file:
        lines = file.readlines()
    
    # Find the first and second occurrences of the buffer calculation section
    start_marker = "                # Extract buffer percentage for display in the output"
    end_marker = "                        stop_loss_buffer_percentage = calculated_buffer"
    
    first_start = -1
    first_end = -1
    second_start = -1
    second_end = -1
    
    for i, line in enumerate(lines):
        if start_marker in line and first_start == -1:
            first_start = i
        elif end_marker in line and first_start != -1 and first_end == -1:
            first_end = i
        elif start_marker in line and first_start != -1 and first_end != -1 and second_start == -1:
            second_start = i
        elif end_marker in line and second_start != -1 and second_end == -1:
            second_end = i
    
    if second_start != -1 and second_end != -1:
        # Remove the duplicated section
        output_lines = lines[:second_start] + lines[second_end+1:]
        
        # Write the fixed content back
        with open('discord_bot.py', 'w') as file:
            file.writelines(output_lines)
        
        print("Fixed: Removed duplicated buffer calculation code")
    else:
        print("No duplicated buffer calculation code found")

if __name__ == "__main__":
    fix_duplicated_buffer_code()