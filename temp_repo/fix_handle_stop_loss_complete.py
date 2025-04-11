"""
Complete fix for the handle_stop_loss_request method in discord_bot.py.
This fix ensures the method properly handles the swing trade case and always returns an embed.
"""

import re

def apply_fix():
    """Apply a comprehensive fix for the handle_stop_loss_request method"""
    with open('discord_bot.py', 'r') as f:
        content = f.read()
    
    # First check which problem we need to fix:
    # Look for trade_type = "Swing Trade" and see if it has the return statement
    if 'trade_type = "Swing Trade"' in content and 'About to return embed from Swing Trade section' not in content:
        # Fix the method with consistent logic, proper return statements,
        # and clear debug statements throughout
        
        # Find the method definition
        pattern = r'async def handle_stop_loss_request\(self, message, info\):(?:.|\n)+?(?=    async def)'
        match = re.search(pattern, content)
        
        if match:
            old_method = match.group(0)
            
            # Create the improved method
            new_method = """async def handle_stop_loss_request(self, message, info):
        \"\"\"Handle requests for stop loss recommendations using Discord embeds for better visual styling\"\"\"
        print("DEBUG: Starting handle_stop_loss_request method")
        print(f"DEBUG: Received info: {info}")
        print("DEBUG: Enhanced debugging enabled for stop_loss_request")
        
        try:
            import inspect
            print(f"DEBUG: Current method at line {inspect.currentframe().f_lineno}")
            
            if 'ticker' not in info or not info['ticker']:
                # Return error for missing ticker
                print("DEBUG: Missing ticker in info")
                import discord
                return discord.Embed(
                    title="Missing Ticker Symbol",
                    description="Please provide a ticker symbol for your stop loss recommendation.",
                    color=0xFF0000  # Red for error
                )
            
            ticker = info['ticker']
            print(f"DEBUG: Processing ticker: {ticker}")
            
            # Get stock data
            import yfinance as yf
            stock = yf.Ticker(ticker)
            
            # Get basic stock price
            try:
                # Try to get current price from info
                current_price = stock.info.get('currentPrice')
                
                # If that fails, get it from history
                if current_price is None:
                    current_price = stock.history(period='1d')['Close'].iloc[-1]
            except Exception as e:
                print(f"Error getting stock price: {str(e)}")
                # Fallback to a default price for testing
                import discord
                return discord.Embed(
                    title="Error Getting Stock Data",
                    description=f"Could not retrieve current price data for {ticker}. Please try again later.",
                    color=0xFF0000  # Red for error
                )
            
            # Get comprehensive stop loss recommendations based on expiration date
            print(f"DEBUG: Getting stop loss recommendations with expiration: {info['expiration']}")
            from technical_analysis import get_stop_loss_recommendation
            stop_loss_recommendations = get_stop_loss_recommendation(
                stock, 
                current_price, 
                info['option_type'], 
                info['expiration']
            )
            print(f"DEBUG: Raw stop_loss_recommendations: {stop_loss_recommendations}")
            
            # Get the primary recommendation which is most appropriate for the option expiration
            primary_recommendation = stop_loss_recommendations.get('primary', {})
            
            # If trade_horizon is explicitly set in info, use it, otherwise get it from recommendations
            if info.get('trade_horizon'):
                print(f"DEBUG: Using explicitly provided trade_horizon: {info['trade_horizon']}")
                trade_horizon = info['trade_horizon']
            else:
                # Determine trade horizon if available 
                trade_horizon = stop_loss_recommendations.get('trade_horizon', 'unknown')
                print(f"DEBUG: Using trade_horizon from recommendations: {trade_horizon}")
            
            # Set the emoji based on the trade horizon
            if trade_horizon == 'scalp':
                horizon_emoji = "⚡"
                horizon_description = "scalp/day trade"
            elif trade_horizon == 'swing':
                horizon_emoji = "📈"
                horizon_description = "swing trade"
            elif trade_horizon == 'longterm':
                horizon_emoji = "🌟"
                horizon_description = "long-term position"
            else:
                horizon_emoji = "🛑"
                horizon_description = "position"
            
            # Get option price data for the exact position
            # We need to get the current price of the option to calculate what it would be worth at the stop loss level
            try:
                # Get option chain
                options = stock.option_chain(info['expiration'])
                
                if info['option_type'].lower() == 'call':
                    chain = options.calls
                else:
                    chain = options.puts
                
                # Find the option with the exact strike price
                option = chain[chain['strike'] == info['strike']]
                
                current_option_price = None
                option_greeks = None
                if not option.empty:
                    current_option_price = option['lastPrice'].iloc[0]
                    print(f"Current option price for {ticker} {info['option_type']} ${info['strike']} expiring {info['expiration']}: ${current_option_price}")
                    
                    # Get option greeks if we can
                    from option_calculator import get_option_greeks
                    try:
                        option_greeks = get_option_greeks(stock, info['expiration'], info['strike'], info['option_type'])
                        print(f"Retrieved option Greeks: {option_greeks}")
                    except Exception as e:
                        print(f"Error getting option Greeks: {str(e)}")
                        option_greeks = None
                else:
                    print(f"Option with strike {info['strike']} not found in chain")
            except Exception as e:
                print(f"Error getting option price data: {str(e)}")
                current_option_price = None
                option_greeks = None
                
            # Import the functions to calculate option price at stop loss and theta decay
            from option_calculator import calculate_option_at_stop_loss, calculate_theta_decay, calculate_expiry_theta_decay
            
            # Create Discord embed for better visual styling with a colored border
            import discord
            
            # Choose color based on trade horizon
            if trade_horizon == 'scalp':
                # Red-orange for scalp (short-term, higher risk)
                embed_color = 0xFF5733
            elif trade_horizon == 'swing':
                # Purple for swing trades
                embed_color = 0x9370DB
            elif trade_horizon == 'longterm':
                # Blue for long-term positions
                embed_color = 0x0099FF
            else:
                # Default teal color for unknown trade horizons
                embed_color = 0x36B37E
                
            print(f"DEBUG: Ticker {ticker}, option_type {info['option_type']}, strike {info['strike']}")
            
            # Create the embed with title and color
            embed = discord.Embed(
                title=f"{horizon_emoji} {ticker} {info['option_type'].upper()} ${info['strike']:.2f} {info['expiration']} {horizon_emoji}",
                description="",
                color=embed_color
            )
            
            # Start building the stop loss recommendation content
            stop_loss_content = f"**Current Stock Price:** ${current_price:.2f}\\n"
            
            # Add current option price if available
            if current_option_price is not None:
                stop_loss_content += f"**Current Option Price:** ${current_option_price:.2f}\\n"
            
            # Only include the primary recommendation's message
            if 'recommendation' in primary_recommendation and 'level' in primary_recommendation:
                stop_loss_level = primary_recommendation['level']
                
                if current_option_price is not None:
                    try:
                        # Calculate estimated option price at stop loss
                        print(f"Using ticker: {ticker} for option calculations")
                        option_at_stop = calculate_option_at_stop_loss(
                            current_stock_price=current_price, 
                            stop_loss_price=stop_loss_level, 
                            strike_price=info['strike'], 
                            current_option_price=current_option_price, 
                            expiration_date=info['expiration'], 
                            option_type=info['option_type'],
                            ticker_symbol=ticker
                        )
                        
                        option_stop_price = option_at_stop['price']
                        percent_change = option_at_stop['percent_change']
                        
                        # Add to stop loss content for the embed
                        stop_loss_content += f"• Stock Price Stop Level: ${stop_loss_level:.2f}\\n"
                        stop_loss_content += f"• Option Price at Stop: ${option_stop_price:.2f} (a {abs(percent_change):.1f}% loss)\\n"
                    except Exception as e:
                        print(f"Error calculating option price at stop loss: {str(e)}")
                        # Fallback to a simplified estimation
                        if info['option_type'].lower() == 'call':
                            price_drop_pct = (current_price - stop_loss_level) / current_price
                            option_stop_price = current_option_price * (1 - (price_drop_pct * 2.5))  # Options typically move 2-3x stock
                        else:
                            price_rise_pct = (stop_loss_level - current_price) / current_price
                            option_stop_price = current_option_price * (1 - (price_rise_pct * 2.5))
                        
                        option_stop_price = max(0, option_stop_price)
                        percent_change = ((option_stop_price - current_option_price) / current_option_price) * 100
                        
                        stop_loss_content += f"• Stock Price Stop Level: ${stop_loss_level:.2f}\\n"
                        stop_loss_content += f"• Option Price at Stop: ${option_stop_price:.2f} (a {abs(percent_change):.1f}% loss)\\n"
                else:
                    stop_loss_content += f"• Stock Price Stop Level: ${stop_loss_level:.2f}\\n"
            else:
                stop_loss_content += f"• Stock Price Stop Level: ${primary_recommendation.get('level', current_price * 0.95):.2f}\\n"
                
            # Add the stop loss recommendation to the embed (non-bolded text)
            embed.add_field(
                name="📊 STOP LOSS RECOMMENDATION 📊",
                value=stop_loss_content,
                inline=False
            )
            
            print(f"DEBUG: Checking trade timeframes - trade_horizon: {trade_horizon}")
            print(f"DEBUG: stop_loss_recommendations keys: {list(stop_loss_recommendations.keys())}")
            
            # Determine most appropriate timeframe based on given trade_horizon
            # Force trade_type setting based on trade_horizon if it was explicitly provided
            if trade_horizon == 'scalp':
                print("DEBUG: Entering SCALP trade section (explicitly set)")
                trade_type = "Scalp/Day Trade"
                print(f"DEBUG: Set trade_type to: {trade_type}")
            elif trade_horizon == 'swing':
                print("DEBUG: Entering SWING trade section (explicitly set)")
                trade_type = "Swing Trade"
                print(f"DEBUG: Set trade_type to: {trade_type}")
            elif trade_horizon == 'longterm':
                print("DEBUG: Entering LONGTERM trade section (explicitly set)")
                trade_type = "Long-Term Position/LEAP"
            else:
                # Fall back to automatic selection based on stop_loss_recommendations
                if 'scalp' in stop_loss_recommendations and ('expiration' not in info or trade_horizon == 'scalp'):
                    print("DEBUG: Entering SCALP trade section")
                    trade_type = "Scalp/Day Trade"
                    print(f"DEBUG: Set trade_type to: {trade_type}")
                elif 'swing' in stop_loss_recommendations and ('expiration' not in info or trade_horizon == 'swing' or trade_horizon == 'unknown'):
                    print("DEBUG: Entering SWING trade section")
                    print(f"DEBUG: trade_horizon={trade_horizon}, 'expiration' in info={'expiration' in info}, swing in recommendations={'swing' in stop_loss_recommendations}")
                    trade_type = "Swing Trade"
                    print(f"DEBUG: Set trade_type to: {trade_type}")
                elif 'longterm' in stop_loss_recommendations and ('expiration' not in info or trade_horizon == 'longterm' or trade_horizon == 'unknown'):
                    trade_type = "Long-Term Position/LEAP"
                else:
                    trade_type = "General Position"
            
            # SECTION 3: Trade Classification with specific title for timeframe
            response = ""
            
            if trade_type == "Scalp/Day Trade":
                response += f"**🔍 SCALP TRADE STOP LOSS (5-15 min chart) 🔍**\\n"
                # Add scalp trade specific info and warning
                response += f"• For very short-term options (0-1 days expiry)\\n"
                response += f"• Technical Basis: Breakout candle low with volatility buffer\\n\\n"
                response += f"**What happens to your option at the stop level?**\\n"
                response += f"⚠️ This option will likely lose 40-60% of its value if held as gamma increases near stop level.\\n"
                
                # Add expiry-specific theta decay warning if we have option data and expiration date
                if current_option_price is not None and option_greeks is not None and 'theta' in option_greeks and info['expiration']:
                    # Use day-by-day theta decay projection until expiry
                    try:
                        theta_decay = calculate_expiry_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            expiration_date=info['expiration'],
                            max_days=1  # Use daily intervals for scalp trades (1 day at a time)
                        )
                        
                        # If we have a significant warning, add it
                        if theta_decay['warning_status']:
                            embed.add_field(
                                name="⏳ THETA DECAY WARNING ⏳",
                                value=theta_decay['warning_message'],
                                inline=False
                            )
                    except Exception as e:
                        print(f"Error in expiry theta decay for scalp fallback: {str(e)}")
                        # Fall back to standard theta decay
                        try:
                            theta_decay = calculate_theta_decay(
                                current_option_price=current_option_price,
                                theta=option_greeks['theta'],
                                days_ahead=0,
                                hours_ahead=6
                            )
                            
                            # If we have a significant warning, add it
                            if theta_decay['warning_status']:
                                embed.add_field(
                                    name="⏳ THETA DECAY WARNING ⏳",
                                    value=theta_decay['warning_message'],
                                    inline=False
                                )
                        except Exception as fallback_error:
                            print(f"Error in fallback theta decay for scalp: {str(fallback_error)}")
                elif current_option_price is not None and option_greeks is not None and 'theta' in option_greeks:
                    # For scalp trades without expiration date, just show hours
                    try:
                        theta_decay = calculate_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            days_ahead=0,
                            hours_ahead=6
                        )
                        
                        # If we have a significant warning, add it
                        if theta_decay['warning_status']:
                            embed.add_field(
                                name="⏳ THETA DECAY WARNING ⏳",
                                value=theta_decay['warning_message'],
                                inline=False
                            )
                    except Exception as e:
                        print(f"Error calculating standard theta decay for scalp: {str(e)}")
                
                # Add the response content to the embed's description
                embed.description = response
                
                print("DEBUG: About to return embed from Scalp/Day Trade")
                print(f"DEBUG: Embed type: {type(embed)}, Has fields: {hasattr(embed, '_fields')}")
                return embed
            
            elif trade_type == "Swing Trade":
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
                
                # Add the response content to the embed's description
                embed.description = response
                
                print("DEBUG: About to return embed from Swing Trade section")
                print(f"DEBUG: Embed type: {type(embed)}, Has fields: {hasattr(embed, '_fields')}")
                
                # Add risk warning to the embed
                embed.add_field(
                    name="⚠️ RISK WARNING ⚠️",
                    value="Options trading involves substantial risk. Past performance does not guarantee future results. Stop loss levels are estimates only.",
                    inline=False
                )
                
                # Return the embed
                return embed
            
            elif trade_type == "Long-Term Position/LEAP":
                response += f"**🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍**\\n"
                # Add long-term specific info and warning
                response += f"• For long-dated options (3+ months expiry)\\n" 
                response += f"• Technical Basis: Major support level with extended volatility buffer\\n\\n"
                response += f"**What happens to your option at the stop level?**\\n"
                response += f"⚠️ This option will likely lose 30-50% of its value if held but it has better chance of recovering compared to short-term options.\\n"
                
                # Add expiry-specific theta decay warning if we have option data and expiration date
                if current_option_price is not None and option_greeks is not None and 'theta' in option_greeks and info['expiration']:
                    # Use day-by-day theta decay projection until expiry
                    try:
                        theta_decay = calculate_expiry_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            expiration_date=info['expiration'],
                            max_days=7  # Use weekly intervals for long-term/LEAPS options
                        )
                        
                        # If we have a significant warning, add it
                        if theta_decay['warning_status']:
                            embed.add_field(
                                name="⏳ THETA DECAY WARNING ⏳",
                                value=theta_decay['warning_message'],
                                inline=False
                            )
                    except Exception as e:
                        print(f"Error in expiry theta decay for long-term trade fallback: {str(e)}")
                        # Fall back to standard theta decay
                        try:
                            theta_decay = calculate_theta_decay(
                                current_option_price=current_option_price,
                                theta=option_greeks['theta'],
                                days_ahead=5,
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
                            print(f"Error in fallback theta decay for long-term: {str(fallback_error)}")
                elif current_option_price is not None and option_greeks is not None and 'theta' in option_greeks:
                    # For long-term trades without expiration date, show standard weekly decay
                    try:
                        theta_decay = calculate_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            days_ahead=5,
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
                        print(f"Error calculating standard theta decay for long-term: {str(e)}")
                
                # Add the response content to the embed's description
                embed.description = response
                
                # Add risk warning
                embed.add_field(
                    name="⚠️ RISK WARNING ⚠️",
                    value="Options trading involves substantial risk. Past performance does not guarantee future results. Stop loss levels are estimates only.",
                    inline=False
                )
                
                print("DEBUG: About to return embed from Long-Term section")
                return embed
            
            else:
                # General position case
                response += f"**🔍 GENERAL STOP LOSS RECOMMENDATION 🔍**\\n"
                response += f"• For any option timeframe\\n"
                response += f"• Technical Basis: Default 5% buffer from current price\\n\\n"
                response += f"**What happens to your option at the stop level?**\\n"
                response += f"⚠️ Options generally lose 50-70% of their value if the stock hits your stop loss price and you continue to hold the position.\\n"
                
                # Add expiry-specific theta decay warning if we have option data and expiration date
                if current_option_price is not None and option_greeks is not None and 'theta' in option_greeks and info['expiration']:
                    # Use day-by-day theta decay projection until expiry
                    try:
                        theta_decay = calculate_expiry_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            expiration_date=info['expiration'],
                            max_days=5  # Show up to 5 days for general options
                        )
                        
                        # If we have a significant warning, add it
                        if theta_decay['warning_status']:
                            embed.add_field(
                                name="⏳ THETA DECAY WARNING ⏳",
                                value=theta_decay['warning_message'],
                                inline=False
                            )
                    except Exception as e:
                        print(f"Error in expiry theta decay for general trade: {str(e)}")
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
                            print(f"Error in fallback theta decay for general trade: {str(fallback_error)}")
                elif current_option_price is not None and option_greeks is not None and 'theta' in option_greeks:
                    # For general position without expiration date, use an average timeframe of 2 days
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
                        print(f"Error calculating standard theta decay: {str(e)}")
                
                # Add the response content to the embed's description
                embed.description = response
                
                # Add risk warning
                embed.add_field(
                    name="⚠️ RISK WARNING ⚠️",
                    value="Options trading involves substantial risk. Past performance does not guarantee future results. Stop loss levels are estimates only.",
                    inline=False
                )
                
                print("DEBUG: About to return embed from General section")
                return embed
            
            # Fallback for any unexpected case - should never reach here
            # But if we do, return a basic embed
            from datetime import datetime
            embed.add_field(
                name="⚠️ RISK WARNING ⚠️",
                value="Options trading involves substantial risk. Past performance does not guarantee future results. Stop loss levels are estimates only.",
                inline=False
            )
            
            # Add footer to the embed
            embed.set_footer(text=f"Data as of {datetime.now().strftime('%Y-%m-%d %H:%M')} | Prices may change quickly during market hours")
        
            # Return the embed instead of the string response
            print("DEBUG: Fallback code reached - returning default embed")
            return embed
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DEBUG: Error in stop loss recommendation: {str(e)}")
            print(f"DEBUG: Full traceback:\\n{error_details}")
            print(f"DEBUG: Exception type: {type(e)}")
            
            # Create a simple error embed with defensive code
            try:
                import discord
                error_embed = discord.Embed(
                    title="Stop Loss Calculation Error",
                    description=f"Sorry, I encountered an error while calculating your stop loss recommendation: {str(e)}\\n\\nPlease try again with a different ticker or option details.",
                    color=0xFF0000  # Red color for error
                )
                return error_embed
            except Exception as embed_error:
                print(f"Error creating error embed: {str(embed_error)}")
                # Since we can't create an embed, create a mock object with a description for testing
                class MockEmbed:
                    def __init__(self, description, title=None, color=None):
                        self.description = description
                        self.title = title or "Stop Loss Calculation Error"
                        self.color = color or 0xFF0000  # Red by default
                        self.fields = []
                        
                    def add_field(self, name="", value="", inline=False):
                        self.fields.append({"name": name, "value": value, "inline": inline})
                        return self
                        
                    def set_footer(self, text=""):
                        self.footer = {"text": text}
                        return self
                
                error_message = (
                    f"Sorry, I encountered an error while calculating your stop loss recommendation: {str(e)}\\n\\n"
                    f"Please try again with a different ticker or option details."
                )
                
                # Create a more complete mock object
                mock_embed = MockEmbed(
                    description=error_message,
                    title="Stop Loss Calculation Error",
                    color=0xFF0000
                )
                
                # Add more mock data to make it look like a full response
                mock_embed.add_field(
                    name="Troubleshooting Tips",
                    value="• Check that the stock ticker is correct\\n• Verify the option details (strike, expiry)",
                    inline=False
                )
                
                from datetime import datetime
                mock_embed.set_footer(text="Data as of " + datetime.now().strftime("%Y-%m-%d %H:%M"))
                
                return mock_embed"""
            
            # Replace the old method with the new method
            updated_content = content.replace(old_method, new_method)
            
            with open('discord_bot.py', 'w') as f:
                f.write(updated_content)
            
            print("Successfully fixed handle_stop_loss_request method")
            return True
    
    print("No fixes needed or pattern not found")
    return False

if __name__ == "__main__":
    apply_fix()