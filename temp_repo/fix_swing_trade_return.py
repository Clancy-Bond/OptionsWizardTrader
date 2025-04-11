"""
Targeted fix for the Swing Trade section of handle_stop_loss_request
This fixes just the Swing Trade section to ensure it properly returns the embed
"""

def fix_swing_trade_return():
    """
    Fix the Swing Trade section in handle_stop_loss_request to ensure it properly returns the embed
    """
    try:
        # First, make a backup of the file if it doesn't already exist
        import os
        if not os.path.exists('discord_bot.py.swing_fix'):
            os.system('cp discord_bot.py discord_bot.py.swing_fix')
        
        # Read the file
        with open('discord_bot.py', 'r') as f:
            lines = f.readlines()
        
        # Find the start of the Swing Trade section
        swing_trade_start = -1
        for i, line in enumerate(lines):
            if "elif trade_type == \"Swing Trade\":" in line:
                swing_trade_start = i
                break
        
        if swing_trade_start == -1:
            print("Could not find Swing Trade section")
            return
        
        # Find the end of the Swing Trade section (where LEAP section starts)
        leap_section_start = -1
        for i in range(swing_trade_start + 1, len(lines)):
            if "elif trade_type == \"Long-Term Position/LEAP\":" in lines[i]:
                leap_section_start = i
                break
        
        if leap_section_start == -1:
            print("Could not find LEAP section")
            return
        
        # Replace the entire Swing Trade section with a corrected version
        new_swing_section = """                elif trade_type == "Swing Trade":
                    response += f"**🔍 SWING TRADE STOP LOSS (4H/Daily chart) 🔍**\\n"
                    # Add extra lines for swing trade only
                    response += f"• For medium-term options (up to 90 days expiry)\\n"
                    response += f"• Technical Basis: Recent support level with ATR-based buffer\\n\\n"
                    response += f"**What happens to your option at the stop level?**\\n"
                    response += f"⚠️ This option will likely lose 60-80% of its value if held due to accelerated delta decay and negative gamma.\\n"
                
                    # Add expiry-specific theta decay warning if we have option data and expiration date
                    if current_option_price is not None and option_greeks is not None and 'theta' in option_greeks and info['expiration']:
                        # Use day-by-day theta decay projection until expiry
                        try:
                            theta_decay = calculate_expiry_theta_decay(
                                current_option_price=current_option_price,
                                theta=option_greeks['theta'],
                                expiration_date=info['expiration'],
                                max_days=2  # Use 2-day intervals for swing trades
                            )
                            
                            # If we have a significant warning, add it
                            if theta_decay['warning_status']:
                                embed.add_field(
                                    name="⏳ THETA DECAY WARNING ⏳",
                                    value=theta_decay['warning_message'],
                                    inline=False
                                )
                        except Exception as e:
                            print(f"Error in expiry theta decay for swing trade fallback: {str(e)}")
                            # Fall back to standard theta decay
                            try:
                                theta_decay = calculate_theta_decay(
                                    current_option_price=current_option_price,
                                    theta=option_greeks['theta'],
                                    days_ahead=2,
                                    hours_ahead=0
                                )
                                
                                # If we have a significant warning, add it
                                if theta_decay['warning_status']:
                                    embed.add_field(
                                        name="⏳ THETA DECAY WARNING ⏳",
                                        value=theta_decay['warning_message'],
                                        inline=False
                                    )
                            except Exception as fallback_error:
                                print(f"Error in fallback theta decay for swing: {str(fallback_error)}")
                    elif current_option_price is not None and option_greeks is not None and 'theta' in option_greeks:
                        # For swing trades without expiration date, show a few days
                        try:
                            theta_decay = calculate_theta_decay(
                                current_option_price=current_option_price,
                                theta=option_greeks['theta'],
                                days_ahead=2,
                                hours_ahead=0
                            )
                            
                            # If we have a significant warning, add it
                            if theta_decay['warning_status']:
                                embed.add_field(
                                    name="⏳ THETA DECAY WARNING ⏳",
                                    value=theta_decay['warning_message'],
                                    inline=False
                                )
                        except Exception as e:
                            print(f"Error calculating standard theta decay for swing: {str(e)}")
                    
                    # Add risk warning to the embed
                    embed.add_field(
                        name="⚠️ RISK WARNING ⚠️",
                        value="Options trading involves substantial risk. Past performance does not guarantee future results. Stop loss levels are estimates only.",
                        inline=False
                    )
                    
                    # Add the response content to the embed's description
                    embed.description = response
                    
                    print("DEBUG: About to return embed from Swing Trade section")
                    print(f"DEBUG: Embed type: {type(embed)}, description: {embed.description[:30]}...")
                    return embed
"""
        
        # Update the lines with our fixed Swing Trade section
        updated_lines = lines[:swing_trade_start] + [new_swing_section] + lines[leap_section_start:]
        
        # Write the updated file
        with open('discord_bot.py', 'w') as f:
            f.writelines(updated_lines)
        
        print("Successfully updated the Swing Trade section in handle_stop_loss_request")
        
    except Exception as e:
        print(f"Error fixing Swing Trade section: {e}")

if __name__ == "__main__":
    fix_swing_trade_return()