"""
Script to fix empty for loops in discord_bot.py
"""

import re

def fix_empty_for_loops():
    """Find all empty for loops and add 'pass' statements"""
    
    # Read the file
    with open('discord_bot.py', 'r') as f:
        lines = f.readlines()
    
    # Find all for loops that don't have an indented block
    i = 0
    changes = 0
    while i < len(lines) - 1:
        line = lines[i]
        # If this is a for loop
        if re.search(r'\s+for\s+.*:', line):
            next_line = lines[i + 1]
            # Check if the next line has the same or less indentation (indicating no block)
            current_indent = len(line) - len(line.lstrip())
            next_indent = len(next_line) - len(next_line.lstrip())
            
            if next_indent <= current_indent:
                # This is an empty for loop - add a pass statement
                indent = ' ' * (current_indent + 4)  # Add 4 spaces for indentation
                pass_line = f"{indent}pass  # Added by fix script\n"
                lines.insert(i + 1, pass_line)
                print(f"Added pass at line {i+1} for '{line.strip()}'")
                changes += 1
                i += 1  # Increment extra because we added a line
        i += 1
    
    # Write the fixed file
    if changes > 0:
        with open('discord_bot.py', 'w') as f:
            f.writelines(lines)
        print(f"Fixed {changes} empty for loops")
    else:
        print("No empty for loops found")

if __name__ == "__main__":
    fix_empty_for_loops()