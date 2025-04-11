"""
A targeted fix that only modifies specific parts of the handle_stop_loss_request method 
to implement the necessary formatting changes without breaking the structure.
"""

import re

def apply_targeted_fix():
    """Apply targeted fixes for specific formatting requirements."""
    try:
        with open('discord_bot.py', 'r') as f:
            content = f.read()
        
        # Save a backup just in case
        with open('discord_bot.py.targeted_formatting_backup', 'w') as f:
            f.write(content)
        
        # Fix 1: Update expiration date formatting
        expiry_format_pattern = r'(# Format for title\s+expiry_display = expiration_str\s+if \'-\' in expiry_display:).*?(# Determine contract count)'
        expiry_format_replacement = r'''# Format for title
            expiry_display = expiration_str
            if '-' in expiry_display:
                # Convert YYYY-MM-DD to YYYY-MMM-DD format
                parts = expiry_display.split('-')
                if len(parts) == 3:
                    year = parts[0]
                    month = int(parts[1])
                    day = parts[2]
                    
                    # Convert month number to name
                    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    try:
                        month_name = months[month - 1]
                        expiry_display = f"{year}-{month_name}-{day}"
                    except:
                        expiry_display = expiry_display
            
            # Determine contract count'''
        
        content = re.sub(expiry_format_pattern, expiry_format_replacement, content, flags=re.DOTALL)
        
        # Fix 2: Update embed color based on trade horizon
        embed_color_pattern = r'(# Create the Discord embed for the response.*?embed = discord\.Embed\().*?(title=f"⭐ {ticker_symbol\.upper\(\)} {option_type\.upper\(\)} \${strike_price:.2f} {expiry_display} ⭐",\s+color=0x0000FF)'
        embed_color_replacement = r'''# Choose the appropriate color based on trade horizon
            embed_color = 0x0000FF  # Blue color default for longterm

            if trade_horizon == 'scalp':
                embed_color = 0xFF5733  # Orange color for scalp trades
            elif trade_horizon == 'swing':
                embed_color = 0x00CC00  # Green color for swing trades
                
            # Create the Discord embed for the response - format to match screenshot
            embed = discord.Embed(
                title=f"⭐ {ticker_symbol.upper()} {option_type.upper()} ${strike_price:.2f} {expiry_display} ⭐",
                color=embed_color'''
        
        content = re.sub(embed_color_pattern, embed_color_replacement, content, flags=re.DOTALL)
        
        # Fix 3: Update trade horizon field with emojis at both beginning and end
        trade_horizon_pattern = r'(if trade_horizon == \'longterm\':\s+embed\.add_field\(\s+name=).*?(,\s+value=.*?inline=False\s+\))'
        trade_horizon_replacement = r'''if trade_horizon == 'longterm':
                    embed.add_field(
                        name=f"🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍"'''
        
        content = re.sub(trade_horizon_pattern, trade_horizon_replacement, content, flags=re.DOTALL)
        
        swing_pattern = r'(elif trade_horizon == \'swing\':\s+embed\.add_field\(\s+name=).*?(,\s+value=.*?inline=False\s+\))'
        swing_replacement = r'''elif trade_horizon == 'swing':
                    embed.add_field(
                        name=f"📈 SWING TRADE STOP LOSS (4H/Daily chart) 📈"'''
        
        content = re.sub(swing_pattern, swing_replacement, content, flags=re.DOTALL)
        
        scalp_pattern = r'(elif trade_horizon == \'scalp\':\s+embed\.add_field\(\s+name=).*?(,\s+value=.*?inline=False\s+\))'
        scalp_replacement = r'''elif trade_horizon == 'scalp':
                    embed.add_field(
                        name=f"⚡ SCALP TRADE STOP LOSS (5-15 min chart) ⚡"'''
        
        content = re.sub(scalp_pattern, scalp_replacement, content, flags=re.DOTALL)
        
        # Fix 4: Update theta decay projection title to use dynamic expiry_display
        theta_title_pattern = r'(name=)"⚠️ THETA DECAY PROJECTION TO \(.*?\) ⚠️"'
        theta_title_replacement = r'\1f"⚠️ THETA DECAY PROJECTION TO ({theta_expiry_display}) ⚠️"'
        
        content = re.sub(theta_title_pattern, theta_title_replacement, content)
        
        # Write the fixed content back to the file
        with open('discord_bot.py', 'w') as f:
            f.write(content)
        
        print("Successfully applied targeted formatting fixes")
        return True
        
    except Exception as e:
        print(f"Error applying targeted formatting fix: {e}")
        return False

if __name__ == "__main__":
    apply_targeted_fix()