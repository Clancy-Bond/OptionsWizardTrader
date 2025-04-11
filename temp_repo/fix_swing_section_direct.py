"""
Direct fix for the Swing Trade section in handle_stop_loss_request
This will correctly solve the return issue by directly modifying the section.
"""

import re

def apply_direct_fix():
    """Apply a direct fix to the Swing Trade section in handle_stop_loss_request"""
    try:
        # Read the file
        with open('discord_bot.py', 'r') as f:
            content = f.read()
        
        # Find the swing trade section
        pattern = r"elif trade_type == \"Swing Trade\":(.*?)elif trade_type == \"Long-Term Position/LEAP\":"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print("Could not find Swing Trade section")
            return
        
        # Get the entire section
        swing_section = match.group(1)
        
        # Create the fixed swing trade section
        fixed_section = """
                elif trade_type == "Swing Trade":
                    # Add swing trade specific guidance
                    response += f"**🔍 SWING TRADE STOP LOSS (4H/Daily chart) 🔍**\\n"
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
                            print(f"Error in expiry theta decay for swing trade: {str(e)}")
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
                            
                    # Add risk warning
                    embed.add_field(
                        name="⚠️ RISK WARNING ⚠️",
                        value="Options trading involves substantial risk. Past performance does not guarantee future results. Stop loss levels are estimates only.",
                        inline=False
                    )
                    
                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Return the embed
                    print("DEBUG: About to return embed from Swing Trade section")
                    return embed
                
                elif trade_type == "Long-Term Position/LEAP\""""
        
        # Replace the section
        new_content = content.replace(match.group(0), fixed_section)
        
        # Write the updated content
        with open('discord_bot.py', 'w') as f:
            f.write(new_content)
        
        print("Successfully fixed the Swing Trade section")
        
    except Exception as e:
        print(f"Error fixing Swing Trade section: {e}")

if __name__ == "__main__":
    apply_direct_fix()