"""
This script removes all the incorrect pass statements in discord_bot.py
that were introduced by the previous fix script.
"""

def remove_incorrect_pass_statements():
    """
    Reads discord_bot.py and removes all lines containing 'pass  # Added by fix script'
    """
    lines_to_remove = [
        1520, 1539, 1576, 1595, 1640, 1659, 1884, 1903, 1923, 1999, 2014, 2030,
        2319, 2334, 2350, 2673, 2688, 3727, 3921, 3923
    ]
    
    # Read the file
    with open('discord_bot.py', 'r') as f:
        lines = f.readlines()
    
    # Remove the pass statements, adjusting for 0-indexing
    for line_num in sorted(lines_to_remove, reverse=True):
        actual_index = line_num - 1
        if actual_index < len(lines) and "pass  # Added by fix script" in lines[actual_index]:
            del lines[actual_index]
    
    # Write the file back
    with open('discord_bot.py', 'w') as f:
        f.writelines(lines)
    
    print(f"Removed {len(lines_to_remove)} incorrect pass statements")

if __name__ == "__main__":
    remove_incorrect_pass_statements()