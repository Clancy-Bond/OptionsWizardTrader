"""
This script will fix the syntax error in the theta decay display code.
"""

def fix_theta_display():
    """
    Directly fixes the syntax error in the discord_bot.py file.
    """
    # Read the file content
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Initialize variables
    fixed_lines = []
    in_formatted_value = False
    
    # Process each line
    for line in lines:
        if 'formatted_value = f"⚠️ THETA DECAY PROJECTION ⚠️' in line:
            # This is where the error starts
            in_formatted_value = True
            # Replace with correct format
            fixed_lines.append('                        formatted_value = f"⚠️ THETA DECAY PROJECTION ⚠️\\n{date_part}\\nYour option is projected to decay over the next 5 weeks:\\n{cleaned_text}"\n')
        elif in_formatted_value and '# Clean up any double newlines or extra spaces' in line:
            # We've reached the end of the problematic section
            in_formatted_value = False
            fixed_lines.append(line)  # Add the current line
        elif in_formatted_value:
            # Skip problematic lines
            continue
        else:
            # Add unchanged lines
            fixed_lines.append(line)
    
    # Write back the fixed content
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.writelines(fixed_lines)
    
    print("Fixed syntax error in theta decay display code.")

if __name__ == "__main__":
    fix_theta_display()