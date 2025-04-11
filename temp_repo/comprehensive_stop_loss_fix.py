"""
A comprehensive fix for the handle_stop_loss_request method in discord_bot.py.
This creates a complete replacement for the method that ensures all code paths return an embed.
"""

import re

def apply_comprehensive_fix():
    """Apply a comprehensive fix to ensure handle_stop_loss_request always returns an embed"""
    try:
        # Read the file
        with open('discord_bot.py', 'r') as f:
            content = f.read()
        
        # Find the method signature
        pattern = r"async def handle_stop_loss_request\(self, message, info\):"
        match = re.search(pattern, content)
        
        if not match:
            print("Could not find handle_stop_loss_request method")
            return
        
        # Find where the method starts
        method_start_pos = match.start()
        
        # Find the next method which marks the end of this one
        next_method_pattern = r"\n    async def \w+"
        next_method_match = re.search(next_method_pattern, content[method_start_pos:])
        
        if not next_method_match:
            print("Could not find the end of handle_stop_loss_request method")
            return
        
        # Get end position relative to the file
        method_end_pos = method_start_pos + next_method_match.start()
        
        # Replace with our updated version
        replacement = """    async def handle_stop_loss_request(self, message, info):
        \"\"\"Handle requests for stop loss recommendations using Discord embeds for better visual styling\"\"\"
        print("DEBUG: Starting handle_stop_loss_request method")
        print(f"DEBUG: Received info: {info}")
        
        try:
            import discord
            import yfinance as yf
            from datetime import datetime
            import inspect
            
            # Extract ticker and validate basic info
            ticker = info['ticker'].upper() if 'ticker' in info else None
            if not ticker:
                raise ValueError("Ticker symbol is required for stop loss calculations")
            
            print(f"DEBUG: Processing ticker: {ticker}")
            
            # Get stop loss recommendations
            stop_loss_recommendations = {}
            if 'expiration' in info and info['expiration']:
                print(f"DEBUG: Getting stop loss recommendations with expiration: {info['expiration']}")
                days_to_expiry = (datetime.strptime(info['expiration'], '%Y-%m-%d') - datetime.now()).days
                print(f"Days to expiration: {days_to_expiry}, Trade horizon: {info.get('trade_horizon', 'auto')}")
                
                stop_loss_recommendations = get_stop_loss_recommendations(
                    ticker, 
                    option_type=info['option_type'],
                    strike_price=info['strike'],
                    expiration_date=info['expiration'],
                    time_horizon=info.get('trade_horizon', None)  # Use provided horizon if available
                )
            else:
                print("DEBUG: Getting stop loss recommendations without expiration")
                stop_loss_recommendations = get_stop_loss_recommendations(
                    ticker, 
                    option_type=info['option_type'],
                    strike_price=info['strike'],
                    time_horizon=info.get('trade_horizon', None)  # Use provided horizon if available
                )
                
            print(f"DEBUG: Raw stop_loss_recommendations: {stop_loss_recommendations}")
            
            # Determine the trade type
            trade_type = None
            
            # If explicit trade_horizon was provided, use it directly
            if 'trade_horizon' in info and info['trade_horizon']:
                print(f"DEBUG: Using explicitly provided trade_horizon: {info['trade_horizon']}")
                trade_horizon = info['trade_horizon']
                if trade_horizon == "scalp":
                    trade_type = "Scalp Trade"
                elif trade_horizon == "swing":
                    trade_type = "Swing Trade"
                elif trade_horizon == "long_term" or trade_horizon == "position":
                    trade_type = "Long-Term Position/LEAP"
            
            # Fall back to primary recommendation if trade_type still not set
            if not trade_type and 'primary' in stop_loss_recommendations:
                time_horizon = stop_loss_recommendations['primary'].get('time_horizon', 'default')
                print(f"DEBUG: Using primary recommendation time_horizon: {time_horizon}")
                
                if time_horizon == "scalp":
                    trade_type = "Scalp Trade"
                elif time_horizon == "swing":
                    trade_type = "Swing Trade"
                elif time_horizon == "position":
                    trade_type = "Long-Term Position/LEAP"
            
            # Final fallback to trade_horizon field
            if not trade_type and 'trade_horizon' in stop_loss_recommendations:
                time_horizon = stop_loss_recommendations['trade_horizon']
                print(f"DEBUG: Using recommendation trade_horizon field: {time_horizon}")
                
                if time_horizon == "scalp":
                    trade_type = "Scalp Trade"
                elif time_horizon == "swing":
                    trade_type = "Swing Trade"
                elif time_horizon == "position":
                    trade_type = "Long-Term Position/LEAP"
            
            # If we still don't have a trade_type, use a general one
            if not trade_type:
                print("DEBUG: No trade type determined, using 'General Position'")
                trade_type = "General Position"
                
            print(f"DEBUG: Final trade_type: {trade_type}")
            
            # Set color based on trade type
            if 'target_price' in info and info['target_price']:
                color = discord.Color.gold()
                title = f"{ticker} {info['option_type'].upper()} ${info['strike']} TARGET PRICE ANALYSIS"
            else:
                # Set color based on trade type
                if trade_type == "Scalp Trade":
                    color = discord.Color.red()
                elif trade_type == "Swing Trade":
                    color = discord.Color.orange()
                elif trade_type == "Long-Term Position/LEAP":
                    color = discord.Color.green()
                else:
                    color = discord.Color.blue()
                
                # Determine title based on premium and contract info
                if 'premium' in info and info['premium'] and 'contracts' in info and info['contracts']:
                    premium = info['premium']
                    contracts = info['contracts']
                    total_cost = premium * 100 * contracts
                    title = f"{ticker} {info['option_type'].upper()} ${info['strike']} - ${total_cost:.2f} TOTAL POSITION"
                else:
                    title = f"{ticker} {info['option_type'].upper()} ${info['strike']} STOP LOSS"
            
            # Calculate expiration display (e.g., "Apr 19th" or "EXPIRED")
            expiry_display = None
            if 'expiration' in info and info['expiration']:
                try:
                    expiry_date = datetime.strptime(info['expiration'], '%Y-%m-%d')
                    if expiry_date < datetime.now():
                        expiry_display = "EXPIRED"
                    else:
                        # Format as "Apr 19th"
                        expiry_display = expiry_date.strftime("%b %d").replace(" 0", " ")
                        
                        # Add ordinal suffix
                        day = expiry_date.day
                        if 4 <= day <= 20 or 24 <= day <= 30:
                            suffix = "th"
                        else:
                            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                        
                        expiry_display += suffix
                except Exception as date_error:
                    print(f"Error formatting expiration date: {date_error}")
                    expiry_display = info['expiration']  # fallback
            
            # Create the initial embed
            if expiry_display:
                # Include expiry in title if available
                embed = discord.Embed(
                    title=f"{title} (Exp: {expiry_display})",
                    description="",
                    color=color
                )
            else:
                # Title without expiry
                embed = discord.Embed(
                    title=title,
                    description="",
                    color=color
                )
            
            # Calculate the current option price and greeks using yfinance
            current_option_price = None
            option_greeks = None
            try:
                # Get stock information
                stock = yf.Ticker(ticker)
                current_price = stock.history(period="1d")['Close'].iloc[-1]
                
                # Get option chain if expiration is provided
                if 'expiration' in info and info['expiration']:
                    # Convert YYYY-MM-DD to datetime
                    expiry_dt = datetime.strptime(info['expiration'], '%Y-%m-%d')
                    
                    # Format as YYYY-MM-DD for yfinance
                    expiry_str = expiry_dt.strftime('%Y-%m-%d')
                    
                    # Get options chain for this expiration
                    try:
                        options = stock.option_chain(expiry_str)
                        
                        # Extract the specific option price based on type and strike
                        if info['option_type'].lower() == 'call':
                            option_data = options.calls
                        else:
                            option_data = options.puts
                            
                        # Find the specific strike price
                        strike_price = float(info['strike'])
                        option_row = option_data[option_data['strike'] == strike_price]
                        
                        if not option_row.empty:
                            # Get last price from the option chain
                            current_option_price = option_row['lastPrice'].values[0]
                            
                            # Get Greeks if available
                            option_greeks = {}
                            greek_columns = ['delta', 'gamma', 'theta', 'vega', 'impliedVolatility']
                            for greek in greek_columns:
                                if greek in option_row.columns:
                                    option_greeks[greek.lower()] = option_row[greek].values[0]
                            
                            print(f"Current option price for {ticker} {info['option_type']} ${info['strike']} expiring {info['expiration']}: ${current_option_price}")
                            print(f"Retrieved option Greeks: {option_greeks}")
                    except Exception as option_error:
                        print(f"Error getting option data: {option_error}")
            except Exception as stock_error:
                print(f"Error getting stock price: {stock_error}")
                
            # Start building the response
            response = ""
            
            print(f"Using ticker: {ticker} for option calculations")
            
            # Handle target price analysis if provided
            if 'target_price' in info and info['target_price']:
                # Target price analysis - different format
                target_price = info['target_price']
                
                response += f"**🎯 TARGET PRICE ANALYSIS FOR {ticker} @ ${target_price} 🎯**\\n\\n"
                
                # Calculate potential option value change
                try:
                    # Get current stock price
                    stock = yf.Ticker(ticker)
                    current_stock_price = stock.history(period="1d")['Close'].iloc[-1]
                    
                    # Calculate percent change to target
                    price_change_pct = (float(target_price) - current_stock_price) / current_stock_price * 100
                    
                    response += f"**Current Stock Price:** ${current_stock_price:.2f}\\n"
                    response += f"**Target Price:** ${target_price}\\n"
                    response += f"**Price Change:** {price_change_pct:+.2f}%\\n\\n"
                    
                    # Add option-specific analysis if we have option data
                    if current_option_price is not None and option_greeks is not None:
                        # Estimate the new option price at target using delta (approximate)
                        if 'delta' in option_greeks:
                            delta = option_greeks['delta']
                            price_change_dollars = float(target_price) - current_stock_price
                            option_price_change = delta * price_change_dollars
                            estimated_new_price = current_option_price + option_price_change
                            
                            # Option price info
                            response += f"**Current Option Price:** ${current_option_price:.2f}\\n"
                            response += f"**Estimated Price at Target:** ${max(0, estimated_new_price):.2f}\\n"
                            
                            # Calculate percent change and profit/loss
                            option_change_pct = (estimated_new_price - current_option_price) / current_option_price * 100
                            
                            if 'premium' in info and info['premium']:
                                premium = float(info['premium'])
                                profit_loss = (estimated_new_price - premium) * 100  # per contract
                                profit_loss_pct = (estimated_new_price - premium) / premium * 100
                                
                                contracts = 1
                                if 'contracts' in info and info['contracts']:
                                    contracts = int(info['contracts'])
                                
                                total_profit_loss = profit_loss * contracts
                                
                                if total_profit_loss > 0:
                                    response += f"**Estimated Profit:** +${total_profit_loss:.2f} (+{profit_loss_pct:+.2f}%)\\n"
                                else:
                                    response += f"**Estimated Loss:** -${abs(total_profit_loss):.2f} ({profit_loss_pct:+.2f}%)\\n"
                            else:
                                # Just show percentage change without profit/loss
                                response += f"**Estimated Change:** {option_change_pct:+.2f}%\\n"
                        else:
                            response += "\\n*Delta not available - cannot estimate price change accurately*\\n"
                except Exception as target_error:
                    print(f"Error in target price analysis: {target_error}")
                    response += f"\\n*Error calculating target price analysis*\\n"
                    
                # Add the response content to the embed description
                embed.description = response
                
                # Add risk warning
                embed.add_field(
                    name="⚠️ RISK WARNING ⚠️", 
                    value="Options trading involves substantial risk. Past performance does not guarantee future results.",
                    inline=False
                )
                
                print("DEBUG: Target price analysis complete, returning embed")
                return embed  # Exit early with target price analysis
                
            # Handle stop loss recommendations based on trade type
            stop_level = None
            option_stop_price = None
            
            if trade_type == "Scalp Trade" and 'scalp' in stop_loss_recommendations:
                stop_level = stop_loss_recommendations['scalp']['level']
                option_stop_price = stop_loss_recommendations['scalp'].get('option_stop_price', None)
                
                response += f"**🔍 SCALP TRADE STOP LOSS (5/15min chart) 🔍**\\n"
                response += f"• For short-term options (daily/same-week expiry)\\n"
                response += f"• Technical Basis: Intraday support levels with aggressive buffer\\n\\n"
                response += f"**What happens to your option at the stop level?**\\n"
                response += f"⚠️ This option will likely lose 40-50% of its value if held due to volatility compression.\\n"
                
            elif trade_type == "Swing Trade" and 'swing' in stop_loss_recommendations:
                stop_level = stop_loss_recommendations['swing']['level']
                option_stop_price = stop_loss_recommendations['swing'].get('option_stop_price', None)
                
                response += f"**🔍 SWING TRADE STOP LOSS (4H/Daily chart) 🔍**\\n"
                response += f"• For medium-term options (up to 90 days expiry)\\n"
                response += f"• Technical Basis: Recent support level with ATR-based buffer\\n\\n"
                response += f"**What happens to your option at the stop level?**\\n"
                response += f"⚠️ This option will likely lose 60-80% of its value if held due to accelerated delta decay and negative gamma.\\n"
            
            elif trade_type == "Long-Term Position/LEAP" and 'position' in stop_loss_recommendations:
                stop_level = stop_loss_recommendations['position']['level']
                option_stop_price = stop_loss_recommendations['position'].get('option_stop_price', None)
                
                response += f"**🔍 LONG-TERM POSITION STOP LOSS (Weekly chart) 🔍**\\n"
                response += f"• For long-term options and LEAPs (90+ days)\\n"
                response += f"• Technical Basis: Major support level with larger buffer\\n\\n"
                response += f"**What happens to your option at the stop level?**\\n"
                response += f"⚠️ This option will likely lose 30-40% of its value if held, but offers room to adjust position.\\n"
                
            else:
                # Fallback to primary recommendation or safe default
                if 'primary' in stop_loss_recommendations:
                    stop_level = stop_loss_recommendations['primary']['level']
                    option_stop_price = stop_loss_recommendations['primary'].get('option_stop_price', None)
                else:
                    # Create a safe default if all else fails
                    stock = yf.Ticker(ticker)
                    current_price = stock.history(period="1d")['Close'].iloc[-1]
                    stop_level = current_price * 0.95  # 5% below current as safe fallback
                
                response += f"**🔍 GENERAL STOP LOSS RECOMMENDATION 🔍**\\n"
                response += f"• For any option timeframe\\n"
                response += f"• Technical Basis: Default buffer from current price\\n\\n"
                response += f"**What happens to your option at the stop level?**\\n"
                response += f"⚠️ Options generally lose 50-70% of their value if the stock hits your stop loss price.\\n"
            
            # Add stock price information
            try:
                stock = yf.Ticker(ticker)
                current_price = stock.history(period="1d")['Close'].iloc[-1]
                
                # Calculate the distance to stop
                price_to_stop = current_price - stop_level
                pct_to_stop = (price_to_stop / current_price) * 100
                
                response += f"\\n**Current Stock Price:** ${current_price:.2f}\\n"
                response += f"**Stop Level:** ${stop_level:.2f}\\n"
                response += f"**Distance to Stop:** {abs(pct_to_stop):.2f}%\\n"
                
                # Add option-specific information if available
                if current_option_price is not None:
                    response += f"**Current Option Price:** ${current_option_price:.2f}\\n"
                    
                    if option_stop_price is not None:
                        response += f"**Estimated Option Value at Stop:** ${option_stop_price:.2f}\\n"
                        
                        # Calculate percent loss at stop
                        if current_option_price > 0:  # Avoid division by zero
                            loss_pct = ((option_stop_price - current_option_price) / current_option_price) * 100
                            response += f"**Estimated Loss at Stop:** {loss_pct:.2f}%\\n"
                    
                    # Add premium-based profit/loss calculations if available
                    if 'premium' in info and info['premium']:
                        premium = float(info['premium'])
                        contracts = 1
                        if 'contracts' in info and info['contracts']:
                            contracts = int(info['contracts'])
                        
                        # Current profit/loss
                        current_pl = (current_option_price - premium) * 100 * contracts
                        current_pl_pct = ((current_option_price - premium) / premium) * 100
                        
                        if current_pl > 0:
                            response += f"**Current Profit:** +${current_pl:.2f} (+{current_pl_pct:.2f}%)\\n"
                        else:
                            response += f"**Current Loss:** -${abs(current_pl):.2f} ({current_pl_pct:.2f}%)\\n"
                        
                        # Profit/loss at stop if option_stop_price is available
                        if option_stop_price is not None:
                            stop_pl = (option_stop_price - premium) * 100 * contracts
                            stop_pl_pct = ((option_stop_price - premium) / premium) * 100
                            
                            response += f"**P/L at Stop:** -${abs(stop_pl):.2f} ({stop_pl_pct:.2f}%)\\n"
            except Exception as price_error:
                print(f"Error getting stock price information: {price_error}")
            
            # Update the embed with the response
            embed.description = response
            
            # Add theta decay warning based on trade type if we have the data
            if current_option_price is not None and option_greeks is not None and 'theta' in option_greeks:
                try:
                    # Use different decay projections based on trade type
                    if trade_type == "Scalp Trade":
                        # Show hourly decay for scalps
                        theta_decay = calculate_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            days_ahead=1,
                            hours_ahead=4
                        )
                    elif trade_type == "Swing Trade" and 'expiration' in info and info['expiration']:
                        # Use 2-day intervals for swing trades
                        theta_decay = calculate_expiry_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            expiration_date=info['expiration'],
                            max_days=2
                        )
                    elif trade_type == "Long-Term Position/LEAP" and 'expiration' in info and info['expiration']:
                        # Use weekly intervals for LEAPs
                        theta_decay = calculate_expiry_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            expiration_date=info['expiration'],
                            max_days=7
                        )
                    else:
                        # Default decay projection
                        theta_decay = calculate_theta_decay(
                            current_option_price=current_option_price,
                            theta=option_greeks['theta'],
                            days_ahead=2,
                            hours_ahead=0
                        )
                    
                    # Add warning if significant
                    if theta_decay and 'warning_status' in theta_decay and theta_decay['warning_status']:
                        embed.add_field(
                            name="⏳ THETA DECAY WARNING ⏳",
                            value=theta_decay['warning_message'],
                            inline=False
                        )
                except Exception as theta_error:
                    print(f"Error calculating theta decay: {theta_error}")
            
            # Always add the risk warning field
            embed.add_field(
                name="⚠️ RISK WARNING ⚠️",
                value="Options trading involves substantial risk. Past performance does not guarantee future results. Stop loss levels are estimates only.",
                inline=False
            )
            
            # Add a footer
            embed.set_footer(text=f"Data as of {datetime.now().strftime('%Y-%m-%d %H:%M')} | Prices may change during market hours")
            
            # Return the completed embed
            print(f"DEBUG: Successfully created {trade_type} embed, returning it now")
            return embed
            
        except Exception as e:
            # Error handling
            import traceback
            error_details = traceback.format_exc()
            print(f"DEBUG: Error in stop loss recommendation: {str(e)}")
            print(f"DEBUG: Full traceback:\\n{error_details}")
            
            # Create an error embed
            try:
                import discord
                error_embed = discord.Embed(
                    title="Stop Loss Calculation Error",
                    description=f"Sorry, I encountered an error while calculating your stop loss recommendation: {str(e)}\\n\\nPlease try again with a different ticker or option details.",
                    color=discord.Color.red()
                )
                return error_embed
            except Exception as embed_error:
                # If we can't create a proper embed, create a mock object
                print(f"Error creating error embed: {str(embed_error)}")
                
                class MockEmbed:
                    def __init__(self, description, title=None, color=None):
                        self.description = description
                        self.title = title or "Stop Loss Calculation Error"
                        self.color = color or 0xFF0000
                        self.fields = []
                        
                    def add_field(self, name="", value="", inline=False):
                        self.fields.append({"name": name, "value": value, "inline": inline})
                        return self
                        
                    def set_footer(self, text=""):
                        self.footer = {"text": text}
                        return self
                
                mock_embed = MockEmbed(
                    description=f"Sorry, I encountered an error while calculating your stop loss recommendation: {str(e)}\\n\\nPlease try again with a different ticker or option details.",
                    title="Stop Loss Calculation Error",
                    color=0xFF0000
                )
                
                return mock_embed
"""
        
        # Update the content with our new method
        new_content = content[:method_start_pos] + replacement + content[method_end_pos:]
        
        # Write the updated content back to the file
        with open('discord_bot.py', 'w') as f:
            f.write(new_content)
        
        print("Successfully applied comprehensive fix to handle_stop_loss_request")
        
    except Exception as e:
        print(f"Error applying comprehensive fix: {e}")

if __name__ == "__main__":
    apply_comprehensive_fix()