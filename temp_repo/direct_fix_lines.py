"""
Direct fix for problematic lines in discord_bot.py
"""

def fix_line_by_line():
    with open('discord_bot.py', 'r') as file:
        lines = file.readlines()
    
    for i in range(len(lines)):
        if i == 1233:  # Line number for first problematic line
            lines[i] = '                                embed.description = f"Your {ticker} ${closest_option[\'strike\']:.2f} {info[\'option_type\']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} ${abs(price_change):.2f} (to ${target_price:.2f}) by {target_date.strftime(\'%B %d, %Y\')}\\n\\n**Current option price:** ${closest_option[\'lastPrice\']:.2f}"\n'
        elif i == 1234 or i == 1235:  # Delete the next two lines that complete the broken string
            lines[i] = ''
        elif i == 1293:  # Line number for second problematic line
            lines[i] = '                                embed.description = f"Your {ticker} ${closest_option[\'strike\']:.2f} {info[\'option_type\']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} {abs(pct_change):.1f}% (to ${target_price:.2f}) by {target_date.strftime(\'%B %d, %Y\')}\\n\\n**Current option price:** ${closest_option[\'lastPrice\']:.2f}"\n'
        elif i == 1294 or i == 1295:  # Delete the next two lines that complete the broken string
            lines[i] = ''
    
    with open('discord_bot.py', 'w') as file:
        file.writelines(lines)
    
    print("Fixed problematic lines in discord_bot.py")

if __name__ == "__main__":
    fix_line_by_line()