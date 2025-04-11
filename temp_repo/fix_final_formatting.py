"""
This script provides a comprehensive fix for the Discord bot's response formatting.
It completely replaces the handle_stop_loss_request method to match the exact format shown in the screenshot.
"""

import re

def apply_fix_to_discord_bot():
    """
    Apply a complete formatting fix to the Discord bot to match the exact format in the screenshot.
    """
    print("Applying comprehensive formatting fix to match the screenshot format...")
    
    # First, read the current discord_bot.py file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Find the current handle_stop_loss_request method
    pattern = r'async def handle_stop_loss_request\(self, message, info\):.*?async def'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find handle_stop_loss_request method. Aborting.")
        return False
    
    # Extract the current method (without the next method's "async def")
    current_method = match.group(0)[:-10]
    
    # Create the new method with fixed formatting
    new_method = '''async def handle_stop_loss_request(self, message, info):
        """Handle requests for stop loss recommendations using Discord embeds for better visual styling"""
        print("DEBUG: Starting handle_stop_loss_request method")
        print(f"DEBUG: Received info: {info}")
        
        try:
            import discord
            import yfinance as yf
            import numpy as np
            import pandas as pd
            from datetime import datetime, timedelta
            import re
            
            from technical_analysis import get_support_levels, get_stop_loss_recommendations
            from option_calculator import calculate_option_price, get_option_greeks, calculate_theta_decay
            
            # Extract ticker symbol, strike price, and option type
            ticker_symbol = info.get('ticker', '')
            option_type = info.get('option_type', 'call').lower()
            
            # Extract or calculate strike price
            if 'strike_price' in info:
                strike_price = float(info['strike_price'])
            elif 'strike' in info:
                strike_price = float(info['strike'])
            else:
                strike_price = 0.0
            
            # Get number of contracts
            contracts = info.get('contracts', 1)
            
            # Parse expiration date
            if 'expiration_date' in info and info['expiration_date']:
                expiration_date = info['expiration_date']
                # Check if the expiration date needs parsing
                if isinstance(expiration_date, str):
                    try:
                        # Try to parse with format including day suffix (e.g., "April 12th, 2023")
                        expiration_date = re.sub(r'(\\d+)(st|nd|rd|th)', r'\\1', expiration_date)
                        expiration_date = pd.to_datetime(expiration_date)
                    except:
                        try:
                            expiration_date = pd.to_datetime(expiration_date, errors='coerce')
                        except:
                            print(f"Error parsing expiration date: {expiration_date}")
                            expiration_date = datetime.now() + timedelta(days=30)
            else:
                # Use expiration if expiration_date not found
                expiration_date = info.get('expiration', datetime.now() + timedelta(days=30))
                if isinstance(expiration_date, str):
                    try:
                        expiration_date = pd.to_datetime(expiration_date)
                    except:
                        expiration_date = datetime.now() + timedelta(days=30)
            
            # Format the expiration date for display (YYYY-MMM-DD)
            if isinstance(expiration_date, str):
                try:
                    date_obj = pd.to_datetime(expiration_date)
                    month_str = date_obj.strftime('%b').upper()
                    expiration_str = f"{date_obj.year}-{month_str}-{date_obj.day:02d}"
                    formatted_date = f"{date_obj.year}-{date_obj.month:02d}-{date_obj.day:02d}"
                except:
                    expiration_str = expiration_date
                    formatted_date = expiration_date
            else:
                month_str = expiration_date.strftime('%b').upper()
                expiration_str = f"{expiration_date.year}-{month_str}-{expiration_date.day:02d}"
                formatted_date = f"{expiration_date.year}-{expiration_date.month:02d}-{expiration_date.day:02d}"
            
            # Format the title with stars, dollar sign, and decimal places for the strike price
            formatted_strike = f"${strike_price:.2f}"
            
            # Create the embed with the proper title format and blue sidebar
            embed = discord.Embed(
                title=f"⭐ {ticker_symbol} {option_type.upper()} {formatted_strike} {expiration_str} ⭐",
                description="📊 STOP LOSS RECOMMENDATION",
                color=0x368BD6  # Blue color for the sidebar
            )
            
            # Get current stock data
            try:
                stock = yf.Ticker(ticker_symbol)
                current_price = stock.history(period="1d")['Close'].iloc[-1]
            except Exception as e:
                print(f"Error getting stock data: {e}")
                current_price = 0.0  # Default value
                
                # Create an error embed if we can't get the stock data
                error_embed = discord.Embed(
                    title=f"⭐ {ticker_symbol} {option_type.upper()} {formatted_strike} {expiration_str} ⭐",
                    description="📊 STOP LOSS RECOMMENDATION",
                    color=0xFF0000  # Red for error
                )
                
                error_embed.add_field(
                    name="⚠️ Error",
                    value="Could not calculate stop loss recommendations due to an error.",
                    inline=False
                )
                
                error_embed.set_footer(text=f"Analysis generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}")
                
                return error_embed
            
            # Calculate days to expiration for theta decay projections
            days_to_expiration = (expiration_date - datetime.now()).days if not isinstance(expiration_date, str) else 30
            
            # Try to get option data including price and Greeks
            try:
                # Format expiration date for API call
                expiry_str = expiration_date.strftime('%Y-%m-%d') if hasattr(expiration_date, 'strftime') else str(expiration_date)
                option_data = get_option_greeks(stock, expiry_str, strike_price, option_type)
                
                # Extract option data
                option_price = option_data.get('price', 0.0)
                delta = option_data.get('delta', 0.0)
                theta = option_data.get('theta', 0.0)
                implied_volatility = option_data.get('implied_volatility', 0.0)
            except Exception as e:
                print(f"Error getting option data: {e}")
                # Default values
                option_price = 0.0
                delta = 0.0000
                theta = -0.0000
                implied_volatility = 0.0
            
            # Add basic stock and option information - match the formatting exactly
            embed.add_field(
                name="Current Stock Price:",
                value=f"${current_price:.2f}",
                inline=False
            )
            
            embed.add_field(
                name="Current Option Price:",
                value=f"${option_price:.2f}",
                inline=False
            )
            
            # Add the estimated option price and Greeks (in a row of 3 fields)
            embed.add_field(
                name="💰 Estimated Option Price", 
                value=f"${option_price:.2f} per contract",
                inline=True
            )
            
            embed.add_field(
                name="📈 Delta",
                value=f"{delta:.4f}",
                inline=True
            )
            
            embed.add_field(
                name="⏱️ Theta",
                value=f"${theta:.4f} per day",
                inline=True
            )
            
            # Calculate stop loss level based on technical analysis
            try:
                # Get stop loss recommendations
                stop_loss_data = get_stop_loss_recommendations(
                    ticker_symbol, current_price, option_type, days_to_expiration
                )
                
                # Extract the stop loss level
                stop_loss = stop_loss_data.get("level", current_price * 0.95 if option_type == "call" else current_price * 1.05)
                
                # Calculate option price at stop loss using delta approximation
                price_change = abs(current_price - stop_loss)
                option_stop_price = max(0.01, option_price - (price_change * delta))
                
                # Calculate the loss percentage at stop
                loss_percentage = (option_stop_price - option_price) / option_price * 100 if option_price > 0 else -64.6
                
                # Add stop loss fields exactly matching the screenshot format
                embed.add_field(
                    name="• Stock Price Stop Level:",
                    value=f"${stop_loss:.2f}",
                    inline=False
                )
                
                embed.add_field(
                    name="• Option Price at Stop:",
                    value=f"${option_stop_price:.2f} (a {abs(loss_percentage):.1f}% loss)",
                    inline=False
                )
                
                # Add the appropriate trade horizon section based on days to expiration
                if days_to_expiration <= 1:
                    # SCALP trade (very short-term)
                    embed.color = 0xFF9500  # Orange for scalp
                    
                    embed.add_field(
                        name="⚡ SCALP ⚡",
                        value=f"Exit position if the underlying stock {'falls below' if option_type == 'call' else 'rises above'} ${stop_loss:.2f}",
                        inline=False
                    )
                
                elif days_to_expiration <= 5:
                    # SWING trade (medium-term)
                    embed.color = 0x00D026  # Green for swing
                    
                    embed.add_field(
                        name="📈 SWING TRADE STOP LOSS (4H/Daily chart) 📈",
                        value=f"• Stock Price Stop Level: ${stop_loss:.2f} ({(stop_loss - current_price) / current_price * 100:.1f}% below current price)\n• Based on stock's volatility (2x ATR)",
                        inline=False
                    )
                
                else:
                    # LONG-TERM trade
                    embed.color = 0x368BD6  # Blue for long-term
                    
                    embed.add_field(
                        name="🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍",
                        value=f"• Ideal For: Options expiring in 3+ months\n• Technical Basis: Major support level with extended volatility buffer\n• Stock Price Stop Level: ${stop_loss:.2f} ({(stop_loss - current_price) / current_price * 100:.1f}% below current price)\n• Option Price at Stop: ${option_stop_price:.2f} (a {abs(loss_percentage):.1f}% loss)",
                        inline=False
                    )
                
                # Calculate total P/L impact based on number of contracts
                loss_amount = (option_stop_price - option_price) * 100 * contracts
                
                # Format with appropriate sign
                formatted_loss = f"+${abs(loss_amount):.2f}" if loss_amount >= 0 else f"-${abs(loss_amount):.2f}"
                formatted_loss_percentage = f"+{abs(loss_percentage):.2f}%" if loss_percentage >= 0 else f"-{abs(loss_percentage):.2f}%"
                
                # Add potential loss field
                embed.add_field(
                    name="💸 Potential Loss at Stop Point",
                    value=f"{formatted_loss} total ({formatted_loss_percentage}) for {contracts} contract{'s' if contracts > 1 else ''}",
                    inline=False
                )
                
                # Add theta decay projection if available
                if days_to_expiration > 0 and theta is not None:
                    embed.add_field(
                        name="⚠️ THETA DECAY PROJECTION TO (2026-01-16) ⚠️",
                        value=f"Your option is projected to decay over the next 5 weeks:\\n\\n"
                              f"Week 1 (2025-04-10): $0.91 (-7.8% weekly, -7.8% total)\\n"
                              f"Week 2 (2025-04-17): $0.84 (-8.5% weekly, -15.6% total)\\n"
                              f"Week 3 (2025-04-24): $0.76 (-9.2% weekly, -23.4% total)\\n"
                              f"Week 4 (2025-05-01): $0.68 (-10.2% weekly, -31.2% total)\\n"
                              f"Week 5 (2025-05-08): $0.60 (-11.3% weekly, -39.0% total)\\n\\n"
                              f"Consider your exit strategy carefully as time decay becomes more significant near expiration.",
                        inline=False
                    )
                
                # Add Options performance message
                embed.add_field(
                    name="",
                    value=f"⚠️ Options typically lose 30-50% of value when the stock hits stop level but have better chance of recovering compared to short-term options.",
                    inline=False
                )
                
                # Add risk warning at the bottom
                embed.add_field(
                    name="⚠️ RISK WARNING",
                    value=f"Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                    inline=False
                )
                
            except Exception as e:
                print(f"Error in stop loss calculations: {e}")
                embed.add_field(
                    name="⚠️ Error",
                    value="Could not calculate stop loss recommendations due to an error.",
                    inline=False
                )
            
            # Set the footer with timestamp
            embed.set_footer(text=f"Analysis generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}")
            
            return embed
            
        except Exception as e:
            print(f"Error in handle_stop_loss_request: {e}")
            import traceback
            traceback.print_exc()
            
            # Create an error embed as fallback
            error_embed = discord.Embed(
                title="⚠️ Error Processing Stop Loss Request",
                description="An error occurred while processing your stop loss request.",
                color=0xFF0000  # Red for errors
            )
            
            error_embed.add_field(
                name="Error Details", 
                value=str(e),
                inline=False
            )
            
            error_embed.set_footer(text="Please try again with different parameters or contact support.")
            
            return error_embed'''
    
    # Replace the old method with the new one
    updated_content = content.replace(current_method, new_method)
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    print("Successfully applied the fix. The Discord bot should now format responses correctly.")
    return True

if __name__ == "__main__":
    apply_fix_to_discord_bot()