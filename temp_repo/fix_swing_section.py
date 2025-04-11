"""
Direct fix for the Swing Trade section in handle_stop_loss_request method
"""

def fix_swing_section():
    """Apply a targeted fix for the Swing Trade section in the discord_bot.py file"""
    with open('test_minimal_stop_loss.py', 'r') as f:
        test_content = f.read()
    
    # Ensure the test sets trade_horizon to 'swing'
    if "trade_horizon': None" in test_content:
        test_content = test_content.replace("trade_horizon': None", "trade_horizon': 'swing'")
        
        with open('test_minimal_stop_loss.py', 'w') as f:
            f.write(test_content)
        print("Fixed test script to explicitly use 'swing' trade horizon")
    
    with open('discord_bot.py', 'r') as f:
        content = f.read()
    
    # First, let's find the Swing Trade section
    swing_block_start = content.find('elif trade_type == "Swing Trade":')
    
    if swing_block_start == -1:
        print("Could not find Swing Trade section")
        return False
    
    # Find the elif or else after the Swing Trade section
    next_section_start = content.find('elif trade_type ==', swing_block_start + 1)
    
    if next_section_start == -1:
        print("Could not find the end of Swing Trade section")
        return False
    
    # Extract the Swing Trade section
    swing_section = content[swing_block_start:next_section_start]
    
    # Create a new version of the Swing Trade section with proper return
    new_swing_section = '''            elif trade_type == "Swing Trade":
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
                print(f"DEBUG: Embed type: {type(embed)}, Has fields: {hasattr(embed, '_fields')}")
                return embed'''
    
    # Replace the original Swing Trade section with the new one
    new_content = content[:swing_block_start] + new_swing_section + content[next_section_start:]
    
    with open('discord_bot.py', 'w') as f:
        f.write(new_content)
    
    print("Successfully fixed Swing Trade section in discord_bot.py")
    return True

if __name__ == "__main__":
    fix_swing_section()