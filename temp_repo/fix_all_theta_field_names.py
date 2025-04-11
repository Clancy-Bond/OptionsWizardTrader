"""
This script fixes all instances of the theta decay field name in discord_bot.py
by replacing f-strings with simpler string concatenation approach.
"""

def fix_all_theta_field_names():
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all instances where the theta decay field is added using an f-string
    # Replace with simpler string concatenation
    find_pattern = 'name=f"⚠️ THETA DECAY PROJECTION TO ({info[\'expiration\']}) ⚠️",'
    replace_pattern = 'name="⚠️ THETA DECAY PROJECTION TO (" + info["expiration"] + ") ⚠️",'
    
    modified_content = content.replace(find_pattern, replace_pattern)
    
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Fixed all theta field names using string concatenation")

if __name__ == "__main__":
    fix_all_theta_field_names()