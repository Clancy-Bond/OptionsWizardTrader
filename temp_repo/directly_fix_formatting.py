"""
Direct and surgical fix for the Discord bot formatting issues.
This script makes very targeted changes to fix specific formatting issues.
"""

def apply_direct_fix():
    # Load the file content from the original backup
    print("Loading discord_bot.py...")
    try:
        with open('discord_bot.py.fixed', 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        # If .fixed doesn't exist, use the original
        with open('discord_bot.py', 'r', encoding='utf-8') as file:
            content = file.read()
    
    print("Making targeted changes...")
    
    # 1. Fix the title format with stars (⭐)
    content = content.replace(
        'title=f"{ticker_symbol.upper()} {option_type.upper()} ${strike_price:.2f} {expiry_display}"',
        'title=f"⭐ {ticker_symbol.upper()} {option_type.upper()} ${strike_price:.2f} {expiry_display} ⭐"'
    )
    
    # 2. Ensure trade horizon sections have emojis at beginning and end
    content = content.replace(
        'name=f"🔍 LONG-TERM STOP LOSS (Weekly chart)"',
        'name=f"🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍"'
    )
    content = content.replace(
        'name=f"📈 SWING TRADE STOP LOSS (4H/Daily chart)"',
        'name=f"📈 SWING TRADE STOP LOSS (4H/Daily chart) 📈"'
    )
    content = content.replace(
        'name=f"⚡ SCALP TRADE STOP LOSS (5-15 min chart)"',
        'name=f"⚡ SCALP TRADE STOP LOSS (5-15 min chart) ⚡"'
    )
    
    # 3. Ensure theta decay section has emojis at beginning and end
    content = content.replace(
        'name=f"⚠️ THETA DECAY PROJECTION TO {theta_expiry_display}"',
        'name=f"⚠️ THETA DECAY PROJECTION TO {theta_expiry_display} ⚠️"'
    )
    
    # 4. Ensure correct embed colors for each trade horizon
    color_code = '''            # Choose the appropriate color based on trade horizon
            embed_color = 0x0000FF  # Blue color default for longterm

            if trade_horizon == 'scalp':
                embed_color = 0xFF5733  # Orange color for scalp trades
            elif trade_horizon == 'swing':
                embed_color = 0x00CC00  # Green color for swing trades
    '''
    
    content = content.replace(
        '            # Choose color based on trade horizon',
        color_code
    )
    
    # 5. Ensure risk warning appears only once at the bottom
    content = content.replace(
        '# Add risk warning at the top',
        '# Risk warning will be added at the bottom only'
    )
    
    content = content.replace(
        'embed.add_field(\n                name="⚠️ RISK WARNING",\n                value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",\n                inline=False\n            )\n            \n            # Start building',
        '# Start building'
    )
    
    # Save the fixed content
    with open('discord_bot.py.final_format_fixed', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Direct format fix applied! Saved to discord_bot.py.final_format_fixed")
    print("Please manually copy this file to discord_bot.py: cp discord_bot.py.final_format_fixed discord_bot.py")

if __name__ == "__main__":
    apply_direct_fix()