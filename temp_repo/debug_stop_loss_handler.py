"""
Debug script specifically focused on the handle_stop_loss_request method
"""
import asyncio
import traceback
import sys
import os
import inspect
from discord_bot import OptionsBot

async def debug_stop_loss_handler():
    print("====== DEBUGGING STOP LOSS HANDLER ======")
    
    # Create bot instance
    bot = OptionsBot()
    
    # Create info dict with complete values
    info = {
        'ticker': 'TSLA',
        'strike': 270.0,
        'option_type': 'call',
        'expiration': '2025-04-04',
        'contract_count': 1
    }
    
    print(f"Query info: {info}")
    
    # Create mock message and user
    class MockChannel:
        async def send(self, content=None, embed=None):
            print("Channel send:")
            if content:
                print(f"- Content: {content}")
            if embed:
                print(f"- Embed title: {getattr(embed, 'title', 'No title')}")
                print(f"- Embed description: {getattr(embed, 'description', 'No description')[:100]}...")
                # Print all fields
                fields = getattr(embed, '_fields', [])
                for field in fields:
                    print(f"  - Field: {field.get('name', 'No name')}")
                    value = field.get('value', 'No value')
                    print(f"    {value[:50]}...")
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.channel = MockChannel()
            self.mentions = [MockUser()]
            
        async def reply(self, content=None, embed=None):
            print("Message reply:")
            if content:
                print(f"- Content: {content}")
            if embed:
                print(f"- Embed title: {getattr(embed, 'title', 'No title')}")
                desc = getattr(embed, 'description', 'No description')
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                print(f"- Embed description: {desc}")
                # Print all fields
                fields = getattr(embed, '_fields', [])
                for field in fields:
                    print(f"  - Field: {field.get('name', 'No name')}")
                    value = field.get('value', 'No value')
                    print(f"    {value[:50]}...")
    
    class MockUser:
        def __init__(self):
            self.id = 1354551896605589584
            self.mention = f"<@{self.id}>"
            self.bot = False
    
    message = MockMessage("<@1354551896605589584> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025")
    
    try:
        print("\n=== CALLING HANDLE_STOP_LOSS_REQUEST ===")
        # Explicitly wrap in try-except to catch internal errors
        try:
            # Modify OptionsBot.handle_stop_loss_request to add debug prints
            original_method = bot.handle_stop_loss_request
            
            async def debug_wrapper(*args, **kwargs):
                print("DEBUG: Entering handle_stop_loss_request")
                try:
                    print("DEBUG: Before calling original method...")
                    print(f"DEBUG: Message: {args[0].content}")
                    print(f"DEBUG: Info: {args[1]}")
                    
                    # Verify expiration date type
                    if 'expiration' in args[1]:
                        print(f"DEBUG: Expiration type: {type(args[1]['expiration'])}, value: {args[1]['expiration']}")
                    
                    # Add a hook before the trade_type is determined
                    original_start = inspect.getsource(original_method).split("\n")[0]
                    print(f"DEBUG: Original method start: {original_start}")
                    
                    # Print execution path information
                    print("DEBUG: About to determine trade horizon based on days to expiration...")
                    
                    # Add a hook to log which trade_type we're getting
                    original_code = inspect.getsource(original_method)
                    print("DEBUG: Adding trade_type monitoring...")
                    
                    # Let's add a simple debug wrapper to the original handle_stop_loss_request method
                    original_method_source = inspect.getsource(original_method)
                    
                    # Insert direct logging into the method at strategic points
                    # 1. When entering determine trade horizon section
                    # 2. When entering determine trade type section
                    # 3. When entering trade_type conditional check
                    
                    # Define the MockEmbed class first
                    class MockEmbed:
                        def __init__(self, description, title=None, color=None):
                            self.description = description
                            self.title = title
                            self.color = color
                            self._fields = []
                            
                        def add_field(self, name="", value="", inline=False):
                            self._fields.append({"name": name, "value": value, "inline": inline})
                            return self
                            
                        def set_footer(self, text=""):
                            self.footer = text
                            return self
                    
                    # First, let's monkey patch the method directly by adding extra debug prints
                    from types import MethodType
                    
                    async def enhanced_debug_method(self, message, info):
                        """Enhanced debug version with added logging for tracking trade_type"""
                        # Most of the implementation is the same as original_method
                        # But we add additional logging and checks
                        
                        print("DEBUG: Enhanced debug method running...")
                        
                        # Existing validation logic from original method...
                        if 'ticker' not in info or not info['ticker']:
                            print("DEBUG: Missing ticker, returning...")
                            embed = MockEmbed(
                                description="⚠️ I need a ticker symbol to recommend a stop loss.",
                                title="More Information Needed",
                                color=0xffcc00  # Amber color for warnings
                            )
                            return embed
                            
                        if 'option_type' not in info or not info['option_type']:
                            print("DEBUG: Missing option_type, returning...")
                            embed = MockEmbed(
                                description="⚠️ I need to know if it's a call or put option to recommend a stop loss.",
                                title="More Information Needed",
                                color=0xffcc00
                            )
                            return embed
                            
                        if 'strike' not in info or not info['strike']:
                            print("DEBUG: Missing strike price, returning...")
                            embed = MockEmbed(
                                description="⚠️ I need a strike price to recommend a stop loss.",
                                title="More Information Needed",
                                color=0xffcc00
                            )
                            return embed
                        
                        # Load ticker data
                        ticker_symbol = info['ticker']
                        print(f"DEBUG: Ticker symbol: {ticker_symbol}")
                        
                        try:
                            import yfinance as yf
                            stock = yf.Ticker(ticker_symbol)
                            current_price = stock.history(period="1d")['Close'].iloc[-1]
                            print(f"DEBUG: Current price: {current_price}")
                        except Exception as e:
                            print(f"DEBUG: Error getting stock data: {str(e)}")
                            embed = MockEmbed(
                                description=f"⚠️ Error fetching data for {ticker_symbol}: {str(e)}",
                                title="Data Error",
                                color=0xff0000
                            )
                            return embed
                            
                        # Create mockup embed
                        embed = MockEmbed(
                            description="",
                            title=f"🛑 Stop Loss Recommendation for {ticker_symbol} ${info['strike']} {info['option_type'].upper()}",
                            color=0xff5c5c
                        )
                        
                        # Parse expiration date and calculate days to expiration
                        expiry_date = None
                        days_to_expiration = None
                        
                        if 'expiration' in info and info['expiration']:
                            try:
                                from datetime import datetime, date
                                expiry_date = datetime.strptime(info['expiration'], "%Y-%m-%d").date()
                                today = date.today()
                                days_to_expiration = (expiry_date - today).days
                                print(f"DEBUG: Days to expiration: {days_to_expiration}")
                            except Exception as e:
                                print(f"DEBUG: Error parsing expiration date: {str(e)}")
                        else:
                            print("DEBUG: No expiration date provided")
                            embed = MockEmbed(
                                description="⚠️ I need an expiration date to recommend a stop loss.",
                                title="More Information Needed",
                                color=0xffcc00
                            )
                            return embed
                        
                        # Get option chain and technical recommendations
                        from technical_analysis import get_stop_loss_recommendations
                        
                        stop_loss_recommendations = get_stop_loss_recommendations(
                            ticker_symbol, 
                            current_price, 
                            info['option_type'],
                            info['expiration']
                        )
                        
                        print(f"DEBUG: Stop loss recommendations: {stop_loss_recommendations}")
                        
                        # Set trade horizon based on days to expiration
                        trade_horizon = 'longterm'  # Default
                        if days_to_expiration <= 3:
                            trade_horizon = 'scalp'
                        elif days_to_expiration <= 14:
                            trade_horizon = 'swing' 
                            
                        print(f"DEBUG: Days to expiration: {days_to_expiration}, Trade horizon: {trade_horizon}")
                        
                        # Build response content
                        response = f"Here's your stop loss recommendation for {ticker_symbol} ${info['strike']} {info['option_type'].upper()} expiring {expiry_date.strftime('%b %d, %Y')}:\n\n"
                        
                        # Check all available timeframes and include the most appropriate one
                        stop_level = None
                        stop_option_price = None
                        percent_loss = None
                        
                        # Determine most appropriate timeframe based on what we have
                        print("DEBUG: About to determine trade_type based on stop_loss_recommendations and trade_horizon...")
                        
                        trade_type = None
                        
                        if 'scalp' in stop_loss_recommendations and ('expiration' not in info or trade_horizon == 'scalp'):
                            print("DEBUG: Setting trade_type to 'Scalp/Day Trade'")
                            scalp_rec = stop_loss_recommendations.get('scalp', {})
                            stop_level = scalp_rec.get('level', current_price * 0.98)
                            response += f"• Stock Price Stop Level: ${stop_level:.2f}\n"
                            trade_type = "Scalp/Day Trade"
                            ideal_for = "Same-day or next-day options"
                            technical_basis = "Breakout candle low with volatility buffer"
                        elif 'swing' in stop_loss_recommendations and ('expiration' in info and trade_horizon == 'swing'):
                            print("DEBUG: Setting trade_type to 'Swing Trade'")
                            swing_rec = stop_loss_recommendations.get('swing', {})
                            stop_level = swing_rec.get('level', current_price * 0.97)
                            response += f"• Stock Price Stop Level: ${stop_level:.2f}\n"
                            trade_type = "Swing Trade"
                            ideal_for = "Options expiring within 1-2 weeks"
                            technical_basis = "Key support level with 1.5 ATR buffer"
                        elif 'longterm' in stop_loss_recommendations:
                            print("DEBUG: Setting trade_type to 'Long-Term Position'")
                            longterm_rec = stop_loss_recommendations.get('longterm', {})
                            stop_level = longterm_rec.get('level', current_price * 0.95)
                            response += f"• Stock Price Stop Level: ${stop_level:.2f}\n"
                            trade_type = "Long-Term Position"
                            ideal_for = "Options expiring in 30+ days"
                            technical_basis = "Major trendline support with 2 ATR buffer"
                        else:
                            print("DEBUG: Setting trade_type to fallback value")
                            # Fallback
                            stop_level = current_price * 0.95
                            response += f"• Stock Price Stop Level: ${stop_level:.2f}\n"
                            trade_type = "General Position"
                            ideal_for = "Any option position"
                            technical_basis = "10% below current price (general guideline)"
                        
                        print(f"DEBUG: Determined trade_type = '{trade_type}'")
                        
                        if trade_type == "Scalp/Day Trade":
                            print("DEBUG: Entering 'Scalp/Day Trade' condition block")
                            # Add other debug prints if needed
                            
                        # At the end, wrap up and return the embed
                        print(f"DEBUG: At end of enhanced debug method. trade_type = '{trade_type}'")
                        print("DEBUG: About to return from enhanced debug method")
                        
                        # Return a known good embed for testing
                        test_embed = MockEmbed(
                            description=f"DEBUG TEST EMBED: trade_type={trade_type}",
                            title=f"🛑 TEST: Stop Loss for {ticker_symbol} ${info['strike']} {info['option_type'].upper()}",
                            color=0xff5c5c
                        )
                        return test_embed
                    
                    # Replace the original method with our enhanced debug method
                    bot.handle_stop_loss_request = MethodType(enhanced_debug_method, bot)
                    
                    # Call the enhanced debug method instead of the original
                    result = await bot.handle_stop_loss_request(message, info)
                    print(f"DEBUG: Returning from handle_stop_loss_request with result type: {type(result)}")
                    if result is None:
                        print("DEBUG: WARNING - The result is None, which indicates the function didn't return an embed properly")
                        print("DEBUG: This might be because we're hitting an early return or exception")
                    else:
                        print(f"DEBUG: Result has title: {getattr(result, 'title', 'No title')}")
                    return result
                except Exception as e:
                    print(f"DEBUG: Exception in handle_stop_loss_request: {str(e)}")
                    traceback.print_exc(file=sys.stdout)
                    raise
            
            # Replace with the debug version temporarily
            bot.handle_stop_loss_request = debug_wrapper
            
            result = await bot.handle_stop_loss_request(message, info)
            print(f"\nResult type: {type(result)}")
            if result:
                if hasattr(result, 'title'):
                    print(f"Result title: {result.title}")
                if hasattr(result, 'description'):
                    print(f"Result description: {result.description[:200]}...")
                # Print all fields if it's an embed
                if hasattr(result, '_fields'):
                    for field in result._fields:
                        print(f"Field: {field.get('name', 'No name')}")
                        value = field.get('value', 'No value')
                        print(f"  {value[:50]}...")
            else:
                print("Result is None")
        except Exception as e:
            print(f"INTERNAL ERROR in handle_stop_loss_request: {str(e)}")
            traceback.print_exc(file=sys.stdout)
    except Exception as e:
        print(f"ERROR calling handle_stop_loss_request: {str(e)}")
        traceback.print_exc(file=sys.stdout)

def main():
    asyncio.run(debug_stop_loss_handler())

if __name__ == "__main__":
    main()