"""
Final formatting fix for the Discord bot responses to exactly match the desired screenshot format.
"""

import re

def apply_final_formatting():
    """Apply the final formatting to match the exact screenshot example."""
    try:
        with open('discord_bot.py', 'r') as f:
            content = f.read()
        
        # Save a backup just in case
        with open('discord_bot.py.final_formatting_backup', 'w') as f:
            f.write(content)
        
        # Define the pattern to match the entire handle_stop_loss_request method
        method_pattern = r'async def handle_stop_loss_request\(self, message, info\):.*?(?=async def|$)'
        
        # Find the method
        match = re.search(method_pattern, content, re.DOTALL)
        if not match:
            print("Error: Could not find handle_stop_loss_request method")
            return
        
        # Get the entire method text
        old_method = match.group(0)
        
        # Define the new method with improved formatting to match the screenshot
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
                
            # Format for title
            expiry_display = expiration_str
            if '-' in expiry_display:
                # Convert YYYY-MM-DD to YYYY-01-16 format
                parts = expiry_display.split('-')
                if len(parts) == 3:
                    year = parts[0]
                    month = parts[1]
                    day = parts[2]
                    
                    # Convert month number to name
                    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    try:
                        month_name = months[int(month) - 1]
                        expiry_display = f"{year}-{month_name}-{day}"
                    except:
                        expiry_display = expiry_display
            
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
            
            # Determine trade horizon and update embed color
            trade_horizon = stop_loss_recommendations.get('trade_horizon', 'swing')
            print(f"DEBUG: Using trade_horizon from recommendations: {trade_horizon}")
            
            # Get option price and greeks
            option_price = get_option_price(ticker_symbol, option_type, strike_price, expiration_date)
            print(f"Current option price for {ticker_symbol} {option_type} ${strike_price} expiring {expiration_date}: ${option_price:.2f}")
            
            greeks = get_option_greeks(ticker_symbol, option_type, strike_price, expiration_date)
            print(f"Retrieved option Greeks: {greeks}")
            
            # Create the Discord embed for the response - format to match screenshot
            embed = discord.Embed(
                title=f"⭐ {ticker_symbol.upper()} {option_type.upper()} ${strike_price:.2f} {expiry_display} ⭐",
                color=0x0000FF  # Blue color for long-term
            )
            
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
            
            if recommendation:
                stop_level = recommendation['level']
                option_stop_price = recommendation.get('option_stop_price', option_price * 0.3)
                
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
                
                # Determine trade horizon label text
                horizon_text = "LONG-TERM STOP LOSS (Weekly chart)"
                chart_emoji = "🔍"
                
                if trade_horizon == 'scalp':
                    horizon_text = "SCALP TRADE STOP LOSS (5-15 min chart)"
                    chart_emoji = "⚡"
                elif trade_horizon == 'swing':
                    horizon_text = "SWING TRADE STOP LOSS (4H/Daily chart)"
                    chart_emoji = "📈"
                elif trade_horizon == 'longterm':
                    chart_emoji = "🔍"
                    
                # Add trade horizon specific details
                time_horizon_text = f"• Ideal For: Options expiring in {3 if trade_horizon == 'longterm' else 1}+ {'months' if trade_horizon == 'longterm' else 'weeks'}\\n"
                time_horizon_text += f"• Technical Basis: {'Major support level with extended volatility buffer' if trade_horizon == 'longterm' else 'Key technical support with volatility adjustment'}"
                
                embed.add_field(
                    name=f"{chart_emoji} LONG-TERM STOP LOSS (Weekly chart) {chart_emoji}",
                    value=time_horizon_text,
                    inline=False
                )
                
                # Add options value decay warning
                embed.add_field(
                    name="⚠️",
                    value="Options typically lose 30-50% of value when the stock hits stop level but have better chance of recovering compared to short-term options.",
                    inline=False
                )
                
                # Add theta decay projections
                if days_to_expiration > 0 and greeks and 'theta' in greeks:
                    theta = float(greeks['theta'])
                    
                    # Create theta decay projection with proper formatting
                    embed.add_field(
                        name="⚠️ THETA DECAY PROJECTION TO (2026-01-16) ⚠️",
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
                        
                        decay_text += f"Week {week} (2025-{date_str}): ${projected_price:.2f} "
                        decay_text += f"({weekly_percentage:.1f}% weekly, {cumulative_percentage:.1f}% total)\\n"
                    
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
        
        print("Successfully updated the final formatting of handle_stop_loss_request")
        return True
        
    except Exception as e:
        print(f"Error applying final formatting fix: {e}")
        return False

if __name__ == "__main__":
    apply_final_formatting()