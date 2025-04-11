"""
Specifically target line 1239 to fix the string formatting issue
"""

def fix_line_1239():
    with open('discord_bot.py', 'r') as file:
        lines = file.readlines()
    
    # Line 1239 has the unterminated string literal
    lines[1238] = '                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)\\n"\n'
    
    # Line 1299 might have the same issue for the percent change case
    lines[1298] = '                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)\\n"\n'
    
    with open('discord_bot.py', 'w') as file:
        file.writelines(lines)
    
    print("Fixed specific line 1239 in discord_bot.py")

if __name__ == "__main__":
    fix_line_1239()