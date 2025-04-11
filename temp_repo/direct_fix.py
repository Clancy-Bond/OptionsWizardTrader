"""
Direct, focused fix for the Discord bot formatting issues.
This script makes specific, targeted changes with no complexity.
"""

import re

def apply_direct_simple_fixes():
    """Apply only the most necessary, direct fixes"""
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # 1. Fix the theta decay projection formatting - make sure there are no extra parentheses
    content = content.replace(
        'name=f"⚠️ THETA DECAY PROJECTION TO ({theta_expiry_display}) ⚠️"',
        'name=f"⚠️ THETA DECAY PROJECTION TO {theta_expiry_display} ⚠️"'
    )
    
    # 2. Remove duplicate risk warnings in error case
    content = content.replace(
        """                # Add risk warning at the bottom even for error case
                embed.add_field(
                    name="⚠️ RISK WARNING",
                    value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                    inline=False
                )""",
        """                # Risk warning will be added below"""
    )
    
    # 3. Ensure proper emoji formatting for all trade horizons
    content = content.replace(
        'name=f"🔍 LONG-TERM STOP LOSS (Weekly chart)",',
        'name=f"🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍",'
    )
    
    content = content.replace(
        'name=f"📈 SWING TRADE STOP LOSS (4H/Daily chart)",',
        'name=f"📈 SWING TRADE STOP LOSS (4H/Daily chart) 📈",'
    )
    
    content = content.replace(
        'name=f"⚡ SCALP TRADE STOP LOSS (5-15 min chart)",',
        'name=f"⚡ SCALP TRADE STOP LOSS (5-15 min chart) ⚡",'
    )
    
    # Write the modified content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Applied direct, simple fixes to discord_bot.py")

if __name__ == "__main__":
    apply_direct_simple_fixes()