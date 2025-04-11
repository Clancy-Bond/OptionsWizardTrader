"""
Script to validate discord_bot.py and fix any indentation issues
"""

import re

def scan_and_fix_indentation():
    """
    Scan discord_bot.py for indentation issues, especially with 'pass' statements
    added by our fix script that might be incorrectly indented.
    """
    with open('discord_bot.py', 'r') as f:
        lines = f.readlines()
    
    lines_to_remove = []
    
    # Find potentially problematic lines added by our fix script
    for i, line in enumerate(lines):
        if "pass  # Added by fix script" in line:
            # Check the context to see if this was added to a comprehension or generator
            # Look at previous line for things like list/dict comprehensions or generators
            prev_line = lines[i-1] if i > 0 else ""
            prev_stripped = prev_line.strip()
            
            # Check if the previous line has patterns indicating a comprehension or generator
            comprehension_patterns = [
                r'for\s+.*\s+in\s+.*\s+if\s+',  # list/dict comprehension with if
                r'for\s+.*\s+in\s+[^\(\)]*$',    # list/dict comprehension without if
                r'\[\s*for\s+',                 # start of list comprehension
                r'\{\s*for\s+',                 # start of dict comprehension
                r'\(\s*for\s+',                 # start of generator expression
                r',\s*for\s+'                   # continuation in comprehension
            ]
            
            for pattern in comprehension_patterns:
                if re.search(pattern, prev_stripped):
                    print(f"Line {i+1} appears to be incorrectly added to a generator/comprehension: '{prev_stripped}'")
                    lines_to_remove.append(i)
                    break
    
    # Remove the problematic lines
    for idx in sorted(lines_to_remove, reverse=True):
        print(f"Removing line {idx+1}: {lines[idx].strip()}")
        del lines[idx]
    
    # Write the fixed file if changes were made
    if lines_to_remove:
        with open('discord_bot.py', 'w') as f:
            f.writelines(lines)
        print(f"Fixed {len(lines_to_remove)} problematic lines")
    else:
        print("No problematic lines found")
    
    # Now check for the specific indentation issue on line 2092
    empty_for_loops = []
    
    for i, line in enumerate(lines):
        if re.search(r'^\s+for\s+.+:.+$', line.strip()):
            # A for loop with something else on the same line - this is suspicious
            print(f"Line {i+1} has a for loop with something else on the same line: '{line.strip()}'")
        
        if i < len(lines) - 1 and re.search(r'^\s+for\s+.+:$', line.strip()):
            # Check the next line's indentation
            current_indent = len(line) - len(line.lstrip())
            next_line = lines[i+1]
            next_indent = len(next_line) - len(next_line.lstrip())
            
            if next_indent <= current_indent and not next_line.strip().startswith('pass'):
                empty_for_loops.append(i)
                print(f"Line {i+1} has an empty for loop: '{line.strip()}'")
    
    # Add pass statements to any remaining empty for loops
    if empty_for_loops:
        for i in empty_for_loops:
            line = lines[i]
            indent = len(line) - len(line.lstrip())
            # Add a pass statement with proper indentation
            pass_line = ' ' * (indent + 4) + 'pass  # Added by validator\n'
            lines.insert(i + 1, pass_line)
            print(f"Added pass statement after line {i+1}")
        
        # Write the fixed file
        with open('discord_bot.py', 'w') as f:
            f.writelines(lines)
        print(f"Fixed {len(empty_for_loops)} empty for loops")

if __name__ == "__main__":
    scan_and_fix_indentation()