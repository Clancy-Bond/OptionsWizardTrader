"""
Final comprehensive formatting fix to ensure all required elements
are properly displayed in the Discord bot responses.

This script ensures:
1. Expiry dates are formatted as "2026-JAN-16" (uppercase month, dashes)
2. Title has stars (⭐) at both beginning and end
3. Theta decay section is included with ⚠️ emojis at beginning and end
4. Trade horizon sections have emojis at beginning and end (🔍/📈/⚡)
5. Embed colors are correct (blue/green/orange based on trade horizon)
6. Risk warning appears once at the bottom
"""

import re
import os

def apply_final_comprehensive_format_fix():
    """Apply all required formatting fixes to ensure proper display"""
    print("Applying comprehensive formatting fixes...")
    
    # Create a backup before making changes
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        original_content = file.read()
        
    backup_file = 'discord_bot.py.format_backup'
    with open(backup_file, 'w', encoding='utf-8') as file:
        file.write(original_content)
    print(f"Created backup at {backup_file}")
    
    # Load the file content
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Fix title formatting to include stars (⭐) at both beginning and end
    # Find title creation pattern in handle_stop_loss_request
    title_pattern = r'title=f"(.*?{ticker_symbol\.upper\(\)}.*?{option_type\.upper\(\)}.*?\${strike_price:.2f}.*?{expiry_display}.*?)",'
    title_replacement = r'title=f"⭐ \1 ⭐",'
    content = re.sub(title_pattern, title_replacement, content)
    
    # 2. Ensure expiry date is formatted as "YYYY-MMM-DD" (ex: 2026-JAN-16)
    # This part is already implemented, but we'll double-check and enhance it
    expiry_format_pattern = r'# Format for title.*?expiry_display = .*?'
    expiry_format_replacement = '''# Format for title - EXACTLY match format from screenshot: "2026-JAN-16"
            expiry_display = expiration_str
            if '-' in expiry_display:
                # Convert YYYY-MM-DD to YYYY-MMM-DD format (month in all caps)
                parts = expiry_display.split('-')
                if len(parts) == 3:
                    year = parts[0]
                    month = parts[1]
                    day = parts[2]
                    
                    # Convert month number to name
                    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    try:
                        month_name = months[int(month) - 1]
                        # Format with day as two digits
                        expiry_display = f"{year}-{month_name}-{int(day):02d}"
                    except:
                        expiry_display = expiry_display
            '''
    content = re.sub(expiry_format_pattern, expiry_format_replacement, content)
    
    # 3. Ensure theta decay section is included with proper formatting
    theta_decay_section_pattern = r'# Add theta decay projections.*?if days_to_expiration > 0.*?theta = float\(greeks\[\'theta\'\]\).*?embed\.add_field\(.*?name=f"(.*?)THETA DECAY PROJECTION TO (.*?)",(.*?)inline=False.*?\)'
    theta_decay_replacement = '''# Add theta decay projections
                if days_to_expiration > 0 and greeks and 'theta' in greeks:
                    theta = float(greeks['theta'])
                    
                    # Create theta decay projection with proper formatting using the actual expiration date
                    # Format expiration date in the format "(2026-JAN-16)" to match screenshot
                    theta_expiry_display = expiry_display
                    
                    embed.add_field(
                        name=f"⚠️ THETA DECAY PROJECTION TO {theta_expiry_display} ⚠️",
                        value=f"Your option is projected to decay over the next 5 weeks:",
                        inline=False
                    )
                    
                    # Calculate weekly decay projections - exact format from screenshot
                    today = datetime.now().date()
                    decay_text = ""
                    
                    projected_price = option_price
                    for week in range(1, 6):
                        days = week * 7
                        date = today + timedelta(days=days)
                        
                        # Calculate weekly decay
                        weekly_decay = theta * 7
                        weekly_percentage = (weekly_decay / projected_price) * 100
                        cumulative_percentage = (weekly_decay * week / option_price) * 100
                        
                        projected_price = max(0.01, projected_price + weekly_decay)
                        
                        # Format the date as MM-DD
                        date_str = f"{date.month:02d}-{date.day:02d}"
                        
                        # Using current year
                        current_year = datetime.now().year
                        decay_text += f"Week {week} ({current_year}-{date_str}): ${projected_price:.2f} "
                        decay_text += f"({weekly_percentage:.1f}% weekly, {cumulative_percentage:.1f}% total)\\n"
                    
                    decay_text += "\\nConsider your exit strategy carefully as time decay becomes more significant near expiration."
                    embed.add_field(
                        name="",
                        value=decay_text,
                        inline=False
                    )'''
    content = re.sub(theta_decay_section_pattern, theta_decay_replacement, content, flags=re.DOTALL)
    
    # 4. Ensure trade horizon sections have emojis at beginning and end (🔍/📈/⚡)
    content = re.sub(
        r'name=f?"(🔍) LONG-TERM STOP LOSS \(Weekly chart\)( 🔍)?"',
        r'name=f"🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍"',
        content
    )
    content = re.sub(
        r'name=f?"(📈) SWING TRADE STOP LOSS \(4H/Daily chart\)( 📈)?"',
        r'name=f"📈 SWING TRADE STOP LOSS (4H/Daily chart) 📈"',
        content
    )
    content = re.sub(
        r'name=f?"(⚡) SCALP TRADE STOP LOSS \(5-15 min chart\)( ⚡)?"',
        r'name=f"⚡ SCALP TRADE STOP LOSS (5-15 min chart) ⚡"',
        content
    )
    
    # 5. Ensure embed colors are correct for each trade horizon
    embed_color_pattern = r'# Choose color based on.*?embed_color = .*?if trade_horizon == \'scalp\'.*?embed_color = (.*?)  # .*?elif trade_horizon == \'swing\'.*?embed_color = (.*?)  # .*?'
    embed_color_replacement = '''# Choose the appropriate color based on trade horizon
            embed_color = 0x0000FF  # Blue color default for longterm

            if trade_horizon == 'scalp':
                embed_color = 0xFF5733  # Orange color for scalp trades
            elif trade_horizon == 'swing':
                embed_color = 0x00CC00  # Green color for swing trades
            '''
    content = re.sub(embed_color_pattern, embed_color_replacement, content, flags=re.DOTALL)
    
    # 6. Ensure risk warning appears once at the bottom and not twice
    # First, remove any risk warnings that appear in the middle of the response
    risk_warning_top_pattern = r'# Add Risk Warning field.*?embed\.add_field\(.*?name="⚠️ RISK WARNING",(.*?)inline=False.*?\)'
    content = re.sub(risk_warning_top_pattern, '', content, flags=re.DOTALL)
    
    # Now ensure the risk warning appears exactly once at the bottom
    risk_warning_pattern = r'# Add risk warning at the BOTTOM only - no duplicates.*?embed\.add_field\(.*?name="⚠️ RISK WARNING",(.*?)inline=False.*?\)'
    if not re.search(risk_warning_pattern, content, flags=re.DOTALL):
        # If pattern not found, add it before the final return statement
        return_pattern = r'# Send the response.*?return embed'
        risk_warning_addition = '''# Add risk warning at the BOTTOM only - no duplicates
                embed.add_field(
                    name="⚠️ RISK WARNING",
                    value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                    inline=False
                )
                
                # Send the response
                print("Sending embed response")
                return embed'''
        content = re.sub(return_pattern, risk_warning_addition, content, flags=re.DOTALL)
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Comprehensive formatting fixes applied!")

if __name__ == "__main__":
    apply_final_comprehensive_format_fix()