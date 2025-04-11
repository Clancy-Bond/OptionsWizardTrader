"""
A comprehensive fix for all formatting issues in discord_bot.py.
This fix will implement all required changes in one go:

1. Format expiration date to "2026-JAN-16" in all caps with dashes
2. Add emoji at both beginning and end of the trade horizon sections (LONG-TERM/SWING/SCALP)
3. Fix the text in each trade horizon section
4. Update the embed colors based on trade horizon (blue/green/orange)
5. Fix option price calculation at stop loss points
6. Make sure the theta decay projection shows correctly with expiration date
"""

import re

def apply_comprehensive_fix():
    """Apply a comprehensive fix to ensure all formatting requirements are met."""
    try:
        with open('discord_bot.py', 'r') as f:
            content = f.read()
        
        # Save a backup just in case
        with open('discord_bot.py.comprehensive_formatting_backup', 'w') as f:
            f.write(content)
        
        # Define the pattern to match the entire handle_stop_loss_request method
        method_pattern = r'(async def handle_stop_loss_request\(self, message, info\):.*?)(?=\s{4}async def|\s{4}def|$)'
        
        # Find the method
        match = re.search(method_pattern, content, re.DOTALL)
        if not match:
            print("Error: Could not find handle_stop_loss_request method")
            return
        
        # Get the entire method text
        old_method = match.group(0)
        
        # Define the new method with improved formatting to match all requirements
        new_method = '''async def handle_stop_loss_request(self, message, info):
        """Handle requests for stop loss recommendations using Discord embeds for better visual styling"""
        print("DEBUG: Starting handle_stop_loss_request method")
        print(f"DEBUG: Received info: {info}")
        
        import discord
        import yfinance as yf
        import numpy as np
        import pandas as pd
        from datetime import datetime, timedelta
        import os
        
        try:
            from technical_analysis import get_stop_loss_recommendations
            from option_calculator import get_option_price, get_option_greeks
            
            # Extract information from the request
            ticker_symbol = info['ticker']
            strike_price = float(info['strike'])
            option_type = info['option_type'].lower()
            
            # Handle expiration date
            if 'expiration' in info and info['expiration']:
                expiration_date = info['expiration']
                # Convert string to datetime if needed
                if isinstance(expiration_date, str):
                    try:
                        expiration_date = pd.to_datetime(expiration_date)
                    except:
                        print(f"Error parsing expiration date: {expiration_date}")
                        expiration_date = datetime.now() + timedelta(days=30)
            else:
                # Default expiration if not provided
                expiration_date = datetime.now() + timedelta(days=30)
            
            # Format for display
            if isinstance(expiration_date, str):
                expiration_str = expiration_date
            else:
                expiration_str = expiration_date.strftime('%Y-%m-%d')
                
            # Format for title - YYYY-MMM-DD format with month in capital letters
            expiry_display = expiration_str
            if '-' in expiry_display:
                # Convert YYYY-MM-DD to YYYY-MMM-DD format
                parts = expiry_display.split('-')
                if len(parts) == 3:
                    year = parts[0]
                    month_num = int(parts[1])
                    day = parts[2]
                    
                    # Convert month number to uppercase name
                    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    month_name = months[month_num - 1]
                    expiry_display = f"{year}-{month_name}-{day}"
            
            # Determine contract count
            contracts = 1
            if 'contract_count' in info and info['contract_count'] and info['contract_count'] > 0:
                contracts = int(info['contract_count'])
            
            # Get current stock data
            stock = yf.Ticker(ticker_symbol)
            current_price = stock.history(period="1d")['Close'].iloc[-1]
            
            # Calculate days until expiration
            if isinstance(expiration_date, str):
                try:
                    expiration_date = pd.to_datetime(expiration_date)
                except:
                    expiration_date = datetime.now() + timedelta(days=30)
            
            days_to_expiration = (expiration_date - datetime.now()).days
            
            if days_to_expiration < 0:
                embed = discord.Embed(
                    title=f"⚠️ Error: {ticker_symbol} {option_type.upper()} ${strike_price} has expired",
                    description="The option appears to have expired. Please check the expiration date.",
                    color=0xFF0000
                )
                return embed
            
            # Get stop loss recommendations
            print(f"DEBUG: Getting stop loss recommendations with expiration: {expiration_date}")
            stop_loss_recommendations = get_stop_loss_recommendations(ticker_symbol, current_price, option_type, days_to_expiration)
            print(f"DEBUG: Raw stop_loss_recommendations: {stop_loss_recommendations}")
            
            # Get initial trade horizon (will be updated later if needed)
            trade_horizon = stop_loss_recommendations.get('trade_horizon', 'swing')
            print(f"DEBUG: Initial trade_horizon from recommendations: {trade_horizon}")
            
            # Get option price and greeks
            option_price = get_option_price(ticker_symbol, option_type, strike_price, expiration_date)
            print(f"Current option price for {ticker_symbol} {option_type} ${strike_price} expiring {expiration_date}: ${option_price:.2f}")
            
            greeks = get_option_greeks(ticker_symbol, option_type, strike_price, expiration_date)
            print(f"Retrieved option Greeks: {greeks}")
            
            # Choose the appropriate recommendation based on trade horizon
            recommendation = None
            stop_level = None
            option_stop_price = None
            
            # Default to long-term for LEAPS options (>6 months out)
            if days_to_expiration > 180 and 'longterm' in stop_loss_recommendations:
                recommendation = stop_loss_recommendations['longterm']
                trade_horizon = 'longterm'
            elif 'swing' in stop_loss_recommendations:
                recommendation = stop_loss_recommendations['swing']
                trade_horizon = 'swing'
            elif 'longterm' in stop_loss_recommendations:
                recommendation = stop_loss_recommendations['longterm']
                trade_horizon = 'longterm'
            elif 'scalp' in stop_loss_recommendations:
                recommendation = stop_loss_recommendations['scalp']
                trade_horizon = 'scalp'
                
            print(f"DEBUG: Final trade_horizon after adjustments: {trade_horizon}")
                
            # Choose the appropriate color based on final trade horizon
            embed_color = 0x0000FF  # Blue color default for longterm

            if trade_horizon == 'scalp':
                embed_color = 0xFF5733  # Orange color for scalp trades
            elif trade_horizon == 'swing':
                embed_color = 0x00CC00  # Green color for swing trades
                
            # Create the Discord embed for the response - format to match screenshot
            embed = discord.Embed(
                title=f"⭐ {ticker_symbol.upper()} {option_type.upper()} ${strike_price:.2f} {expiry_display} ⭐",
                color=embed_color
            )
            
            if recommendation:
                stop_level = recommendation['level']
                
                # Calculate the option price at the stop level using proper option pricing model
                try:
                    from option_calculator import calculate_option_price, get_option_greeks
                    
                    # Get option greeks for the calculation
                    greeks = get_option_greeks(ticker_symbol, option_type, strike_price, expiration_date)
                    
                    # Calculate days to expiration
                    today = datetime.now().date()
                    expiry_date = datetime.strptime(expiration_date, '%Y-%m-%d').date() if isinstance(expiration_date, str) else expiration_date.date()
                    days_to_expiration = max(1, (expiry_date - today).days)
                    
                    # Calculate the new option price at the stop level
                    option_stop_price = calculate_option_price(
                        current_price=current_price,
                        target_price=stop_level,
                        strike_price=strike_price,
                        greeks=greeks,
                        days_to_expiration=days_to_expiration,
                        option_type=option_type
                    )
                except Exception as e:
                    print(f"Error calculating option price at stop: {e}")
                    # Fallback calculation if the proper method fails
                    if option_type.lower() == 'call':
                        # For calls, lower stock price means lower option price (typically ~Delta% of stock move)
                        price_change_pct = (stop_level - current_price) / current_price
                        option_stop_price = max(0.01, option_price * (1 + price_change_pct))
                    else:
                        # For puts, lower stock price means higher option price (inverse relationship)
                        price_change_pct = (current_price - stop_level) / current_price
                        option_stop_price = max(0.01, option_price * (1 + price_change_pct))
                
                # Calculate loss
                loss_amount = (option_stop_price - option_price) * 100 * contracts
                loss_percentage = ((option_stop_price - option_price) / option_price * 100) if option_price > 0 else 0
                
                # Main STOP LOSS RECOMMENDATION section - EXACT format from screenshot
                stop_loss_text = f"Current Stock Price: ${current_price:.2f}\\n"
                stop_loss_text += f"Current Option Price: ${option_price:.2f}\\n"
                stop_loss_text += f"• Stock Price Stop Level: ${stop_level:.2f}\\n"
                stop_loss_text += f"• Option Price at Stop: ${option_stop_price:.2f} (a {abs(loss_percentage):.1f}% loss)"
                
                embed.add_field(
                    name="📊 STOP LOSS RECOMMENDATION",
                    value=stop_loss_text,
                    inline=False
                )
                
                # Add proper trade horizon field with emoji at both beginning and end
                if trade_horizon == 'longterm':
                    embed.add_field(
                        name=f"🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍",
                        value=f"• Ideal For: Options expiring in 3+ months\\n• Technical Basis: Major support level with extended volatility buffer",
                        inline=False
                    )
                elif trade_horizon == 'swing':
                    embed.add_field(
                        name=f"📈 SWING TRADE STOP LOSS (4H/Daily chart) 📈",
                        value=f"• Ideal For: Options expiring in 1+ weeks\\n• Technical Basis: Key technical support with volatility adjustment",
                        inline=False
                    )
                elif trade_horizon == 'scalp':
                    embed.add_field(
                        name=f"⚡ SCALP TRADE STOP LOSS (5-15 min chart) ⚡",
                        value=f"• Ideal For: Options expiring in 1+ weeks\\n• Technical Basis: Key technical support with volatility adjustment",
                        inline=False
                    )
                
                # Add options value decay warning
                embed.add_field(
                    name="⚠️",
                    value="Options typically lose 30-50% of value when the stock hits stop level but have better chance of recovering compared to short-term options.",
                    inline=False
                )
                
                # Add theta decay projections with proper time intervals based on trade horizon
                if days_to_expiration > 0 and greeks and 'theta' in greeks:
                    theta = float(greeks['theta'])
                    
                    # Create theta decay projection with proper formatting using the actual expiration date
                    theta_expiry_display = expiry_display
                    
                    embed.add_field(
                        name=f"⚠️ THETA DECAY PROJECTION TO ({theta_expiry_display}) ⚠️",
                        value=f"Your option is projected to decay over the next 5 weeks:",
                        inline=False
                    )
                    
                    # Calculate decay projections based on trade horizon
                    today = datetime.now().date()
                    decay_text = ""
                    
                    # Set up intervals based on trade horizon
                    intervals = 7  # Default weekly intervals for long-term
                    interval_label = "Week"
                    
                    if trade_horizon == 'swing':
                        intervals = 2  # 2-day intervals for swing trades
                        interval_label = "Day"
                    elif trade_horizon == 'scalp':
                        intervals = 1  # Daily intervals for scalp trades
                        interval_label = "Day"
                    
                    projected_price = option_price
                    for i in range(1, 6):
                        days_forward = i * intervals
                        date = today + timedelta(days=days_forward)
                        
                        # Calculate decay for the interval
                        interval_decay = theta * intervals
                        interval_percentage = (interval_decay / projected_price) * 100
                        cumulative_percentage = (interval_decay * i / option_price) * 100
                        
                        projected_price = max(0.01, projected_price + interval_decay)
                        
                        # Format the date as MM-DD
                        date_str = f"{date.month:02d}-{date.day:02d}"
                        
                        # Using current year from datetime.now()
                        current_year = datetime.now().year
                        decay_text += f"{interval_label} {i} ({current_year}-{date_str}): ${projected_price:.2f} "
                        decay_text += f"({interval_percentage:.1f}% per {interval_label.lower()}, {cumulative_percentage:.1f}% total)\\n"
                    
                    decay_text += "\\nConsider your exit strategy carefully as time decay becomes more significant near expiration."
                    embed.add_field(
                        name="",
                        value=decay_text,
                        inline=False
                    )
                
                # Add risk warning at the BOTTOM only - no duplicates
                embed.add_field(
                    name="⚠️ RISK WARNING",
                    value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚠️ Error",
                    value="Could not generate stop loss recommendations. Please try again with a different option.",
                    inline=False
                )
                
                # Add risk warning at the bottom even for error case
                embed.add_field(
                    name="⚠️ RISK WARNING",
                    value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                    inline=False
                )
            
            # Send the response
            print("Sending embed response")
            return embed
            
        except Exception as e:
            print(f"Error in handle_stop_loss_request: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
            # Create error embed
            error_embed = discord.Embed(
                title="⚠️ Error Processing Stop Loss Request",
                description=f"An error occurred while processing your stop loss request: {str(e)}",
                color=0xFF0000
            )
            
            # Add risk warning at the bottom even for error case
            error_embed.add_field(
                name="⚠️ RISK WARNING",
                value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                inline=False
            )
            
            return error_embed'''
        
        # Replace the old method with the new one
        updated_content = content.replace(old_method, new_method)
        
        # Write the fixed content back to the file
        with open('discord_bot.py', 'w') as f:
            f.write(updated_content)
        
        print("Successfully applied comprehensive formatting fixes to handle_stop_loss_request")
        return True
        
    except Exception as e:
        print(f"Error applying comprehensive formatting fix: {e}")
        return False

if __name__ == "__main__":
    apply_comprehensive_fix()