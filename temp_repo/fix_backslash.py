"""
Fix the backslash issue in f-strings in discord_bot.py
"""

import re

def fix_discord_bot():
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace f-strings with backslashes with a corrected version
    modified_content = re.sub(
        r'name=f"⚠️ THETA DECAY PROJECTION TO \(\{info\[\\\'expiration\\\'\]\}\) ⚠️",',
        r'name=f"⚠️ THETA DECAY PROJECTION TO ({info[\"expiration\"]}) ⚠️",',
        content
    )
    
    # Another approach if the above doesn't match
    if modified_content == content:
        modified_content = content.replace(
            r"name=f\"⚠️ THETA DECAY PROJECTION TO ({info[\'expiration\']}) ⚠️\",",
            r'name=f"⚠️ THETA DECAY PROJECTION TO ({info[\"expiration\"]}) ⚠️",'
        )
    
    # Direct manual replacement if needed
    if modified_content == content:
        patterns = [
            (r"name=f\"⚠️ THETA DECAY PROJECTION TO ({info[\\\'expiration\\\']}) ⚠️\",", 
             r'name=f"⚠️ THETA DECAY PROJECTION TO ({info[\"expiration\"]}) ⚠️",'),
            (r"name=f\"⚠️ THETA DECAY PROJECTION TO ({info['expiration']}) ⚠️\",", 
             r'name=f"⚠️ THETA DECAY PROJECTION TO ({info[\"expiration\"]}) ⚠️",'),
        ]
        
        for old, new in patterns:
            modified_content = modified_content.replace(old, new)
    
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(modified_content)

if __name__ == "__main__":
    fix_discord_bot()
    print("Fixed backslash issues in f-strings")