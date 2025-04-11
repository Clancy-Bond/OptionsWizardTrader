"""
Fix all instances of f-string quotes in discord_bot.py
"""

def fix_f_strings():
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace all instances of the problematic f-string with fixed version
    modified_content = content.replace(
        "name=f\"⚠️ THETA DECAY PROJECTION TO ({info[\\'expiration\\']}) ⚠️\",",
        "name=f\"⚠️ THETA DECAY PROJECTION TO ({info['expiration']}) ⚠️\","
    )
    
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Fixed all f-string instances")

if __name__ == "__main__":
    fix_f_strings()