"""
Final fix for the handle_stop_loss_request method to ensure it always returns an embed object.
This script will create a complete rewrite with simplified logic and properly structured return statements.
"""

import re

def apply_final_fix():
    """Apply a complete fix for the handle_stop_loss_request method"""
    try:
        with open('discord_bot.py', 'r') as f:
            content = f.read()
        
        # Save a backup just in case
        with open('discord_bot.py.before_final_fix', 'w') as f:
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
        
        # Define the new method with improved structure and error handling
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
        
        # Create a Discord embed for the response
        embed = discord.Embed(
            title=f"🛑 Stop Loss Analysis for {info['ticker']} {info['strike']} {info['option_type']}s",
            description=f"Analysis based on technical indicators and option greeks.",
            color=0xFF5733  # Red color for stop loss
        )
        
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
                expiration_str = expiration_date.strftime('%B %d, %Y')
            
            # Determine contract count
            contracts = 1
            if 'contract_count' in info and info['contract_count'] and info['contract_count'] > 0:
                contracts = int(info['contract_count'])
            
            # Get current stock data
            stock = yf.Ticker(ticker_symbol)
            current_price = stock.history(period="1d")['Close'].iloc[-1]
            
            # Add basic information fields to the embed
            embed.add_field(
                name="📊 Current Stock Price",
                value=f"${current_price:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Strike Price",
                value=f"${strike_price:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="📅 Expiration Date",
                value=f"{expiration_str}",
                inline=True
            )
            
            # Calculate days until expiration
            if isinstance(expiration_date, str):
                try:
                    expiration_date = pd.to_datetime(expiration_date)
                except:
                    expiration_date = datetime.now() + timedelta(days=30)
            
            days_to_expiration = (expiration_date - datetime.now()).days
            
            if days_to_expiration < 0:
                embed.add_field(
                    name="⚠️ Warning",
                    value="The option appears to have expired. Please check the expiration date.",
                    inline=False
                )
                return embed
            
            # Get stop loss recommendations
            print(f"DEBUG: Getting stop loss recommendations with expiration: {expiration_date}")
            stop_loss_recommendations = get_stop_loss_recommendations(ticker_symbol, current_price, option_type, days_to_expiration)
            print(f"DEBUG: Raw stop_loss_recommendations: {stop_loss_recommendations}")
            
            # Determine trade horizon and update embed color
            trade_horizon = stop_loss_recommendations.get('trade_horizon', 'swing')
            print(f"DEBUG: Using trade_horizon from recommendations: {trade_horizon}")
            
            if trade_horizon == 'scalp':
                embed.color = 0x00FF00  # Green
            elif trade_horizon == 'swing':
                embed.color = 0xFFA500  # Orange
            else:  # longterm
                embed.color = 0x0000FF  # Blue
            
            # Get option price and greeks
            option_price = get_option_price(ticker_symbol, option_type, strike_price, expiration_date)
            print(f"Current option price for {ticker_symbol} {option_type} ${strike_price} expiring {expiration_date}: ${option_price:.2f}")
            
            greeks = get_option_greeks(ticker_symbol, option_type, strike_price, expiration_date)
            print(f"Retrieved option Greeks: {greeks}")
            
            # Add option price field
            embed.add_field(
                name="💰 Current Option Price",
                value=f"${option_price:.2f} per contract",
                inline=True
            )
            
            # Add Greek values if available
            if greeks and 'delta' in greeks:
                embed.add_field(
                    name="📈 Delta",
                    value=f"{float(greeks['delta']):.4f}",
                    inline=True
                )
            
            if greeks and 'theta' in greeks:
                embed.add_field(
                    name="⏱️ Theta",
                    value=f"${float(greeks['theta']):.4f} per day",
                    inline=True
                )
            
            # Add stop loss recommendation based on trade horizon
            if trade_horizon in stop_loss_recommendations:
                # Get recommendation data for the specific horizon
                recommendation_data = stop_loss_recommendations[trade_horizon]
                stop_loss_price = recommendation_data['level']
                recommendation_text = recommendation_data['recommendation']
                option_stop_price = recommendation_data.get('option_stop_price', option_price * 0.6)
                
                # Calculate loss
                loss_amount = (option_stop_price - option_price) * 100 * contracts
                loss_percentage = (option_stop_price - option_price) / option_price * 100 if option_price > 0 else 0
                
                # Format with sign
                formatted_loss = f"+${abs(loss_amount):.2f}" if loss_amount >= 0 else f"-${abs(loss_amount):.2f}"
                formatted_loss_percentage = f"+{abs(loss_percentage):.2f}%" if loss_percentage >= 0 else f"-{abs(loss_percentage):.2f}%"
                
                # Add recommendation fields
                if trade_horizon == 'scalp':
                    embed.add_field(
                        name="🛑 Recommended Stop Loss (Day Trade) 🛑",
                        value=f"Exit position if the underlying stock {'falls below' if option_type == 'call' else 'rises above'} ${stop_loss_price:.2f}\\n"
                              f"This corresponds to an option price of approximately ${option_stop_price:.2f}",
                        inline=False
                    )
                    
                    # Add potential loss field
                    embed.add_field(
                        name="💸 Potential Loss at Stop Point",
                        value=f"{formatted_loss} total ({formatted_loss_percentage}) for {contracts} contract{'s' if contracts > 1 else ''}",
                        inline=False
                    )
                    
                    # Add theta decay for scalp (daily intervals)
                    if days_to_expiration > 0 and greeks and 'theta' in greeks:
                        theta = float(greeks['theta'])
                        theta_decay_days = min(days_to_expiration, 5)  # Show up to 5 days for scalps
                        theta_decay_projections = []
                        
                        for day in range(1, theta_decay_days + 1):
                            theta_impact = theta * day * 100 * contracts
                            projected_value = option_price * 100 * contracts - theta_impact
                            theta_decay_projections.append(
                                f"Day {day}: ${projected_value:.2f} ({'-' if theta_impact > 0 else '+'}"
                                f"${abs(theta_impact):.2f})"
                            )
                        
                        embed.add_field(
                            name="⏱️ Theta Decay Projection (Daily) ⏱️",
                            value="\\n".join(theta_decay_projections),
                            inline=False
                        )
                
                elif trade_horizon == 'swing':
                    embed.add_field(
                        name="🛑 Recommended Stop Loss (Swing Trade) 🛑",
                        value=f"Exit position if the underlying stock {'falls below' if option_type == 'call' else 'rises above'} ${stop_loss_price:.2f}\\n"
                              f"This corresponds to an option price of approximately ${option_stop_price:.2f}",
                        inline=False
                    )
                    
                    # Add potential loss field
                    embed.add_field(
                        name="💸 Potential Loss at Stop Point",
                        value=f"{formatted_loss} total ({formatted_loss_percentage}) for {contracts} contract{'s' if contracts > 1 else ''}",
                        inline=False
                    )
                    
                    # Add theta decay for swing (2-day intervals)
                    if days_to_expiration > 0 and greeks and 'theta' in greeks:
                        theta = float(greeks['theta'])
                        theta_decay_days = min(days_to_expiration, 10)  # Show up to 10 days for swing trades
                        theta_decay_projections = []
                        
                        for day in range(2, theta_decay_days + 1, 2):  # 2-day intervals
                            theta_impact = theta * day * 100 * contracts
                            projected_value = option_price * 100 * contracts - theta_impact
                            theta_decay_projections.append(
                                f"Day {day}: ${projected_value:.2f} ({'-' if theta_impact > 0 else '+'}"
                                f"${abs(theta_impact):.2f})"
                            )
                        
                        embed.add_field(
                            name="⏱️ Theta Decay Projection (2-Day Intervals) ⏱️",
                            value="\\n".join(theta_decay_projections),
                            inline=False
                        )
                
                else:  # longterm
                    embed.add_field(
                        name="🛑 Recommended Stop Loss (Long-Term) 🛑",
                        value=f"Exit position if the underlying stock {'falls below' if option_type == 'call' else 'rises above'} ${stop_loss_price:.2f}\\n"
                              f"This corresponds to an option price of approximately ${option_stop_price:.2f}",
                        inline=False
                    )
                    
                    # Add potential loss field
                    embed.add_field(
                        name="💸 Potential Loss at Stop Point",
                        value=f"{formatted_loss} total ({formatted_loss_percentage}) for {contracts} contract{'s' if contracts > 1 else ''}",
                        inline=False
                    )
                    
                    # Add theta decay for long-term (weekly intervals)
                    if days_to_expiration > 0 and greeks and 'theta' in greeks:
                        theta = float(greeks['theta'])
                        weeks_to_show = min(days_to_expiration // 7 + 1, 8)  # Show up to 8 weeks
                        theta_decay_projections = []
                        
                        for week in range(1, weeks_to_show + 1):
                            days = week * 7
                            theta_impact = theta * days * 100 * contracts
                            projected_value = option_price * 100 * contracts - theta_impact
                            theta_decay_projections.append(
                                f"Week {week}: ${projected_value:.2f} ({'-' if theta_impact > 0 else '+'}"
                                f"${abs(theta_impact):.2f})"
                            )
                        
                        embed.add_field(
                            name="⏱️ Theta Decay Projection (Weekly) ⏱️",
                            value="\\n".join(theta_decay_projections),
                            inline=False
                        )
            
            # Always add risk warning at the end
            embed.add_field(
                name="⚠️ RISK WARNING ⚠️",
                value="These stop loss recommendations are based on technical analysis and should be used as a guideline only. "
                      "Always consider your personal risk tolerance and market conditions before making trading decisions.",
                inline=False
            )
            
            # Set footer with timestamp
            embed.set_footer(text=f"Analysis generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}")
            
            return embed
            
        except Exception as e:
            print(f"Error in handle_stop_loss_request: {e}")
            
            # Create error embed
            error_embed = discord.Embed(
                title="⚠️ Error Processing Stop Loss Request",
                description="An error occurred while processing your stop loss request.",
                color=0xFF0000
            )
            error_embed.add_field(
                name="Error Details",
                value=str(e),
                inline=False
            )
            error_embed.set_footer(text="Please try again with different parameters or contact support.")
            
            return error_embed'''
        
        # Replace the old method with the new one
        updated_content = content.replace(old_method, new_method)
        
        # Write the fixed content back to the file
        with open('discord_bot.py', 'w') as f:
            f.write(updated_content)
        
        print("Successfully applied final fix to handle_stop_loss_request")
        return True
        
    except Exception as e:
        print(f"Error applying fix: {e}")
        return False

if __name__ == "__main__":
    apply_final_fix()