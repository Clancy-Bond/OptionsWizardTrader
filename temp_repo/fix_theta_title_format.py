"""
Fix the THETA DECAY PROJECTION title formatting in discord_bot.py
This script ensures that:
1. The field name remains "⚠️ THETA DECAY PROJECTION ⚠️"
2. The line with the date "THETA DECAY PROJECTION TO (date)" is bold and has emojis on both sides
"""

def fix_theta_decay_title_format():
    """
    Update all instances of the theta decay warning replacement logic
    to ensure proper formatting of the title with the date.
    """
    print("Fixing theta decay title formatting...")
    
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all instances of the string pattern we want to replace
    old_pattern = 'value=theta_decay["warning_message"].replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ THETA DECAY PROJECTION TO").replace("** ⚠️", ""),'
    new_pattern = 'value=theta_decay["warning_message"].replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ **THETA DECAY PROJECTION TO").replace("** ⚠️", "** ⚠️"),'
    
    # Replace all instances
    updated_content = content.replace(old_pattern, new_pattern)
    
    # Check how many replacements were made
    original_count = content.count(old_pattern)
    updated_count = updated_content.count(new_pattern)
    
    print(f"Found and replaced {original_count} instances of the theta decay title pattern")
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("Theta decay title formatting fixed!")

if __name__ == "__main__":
    fix_theta_decay_title_format()