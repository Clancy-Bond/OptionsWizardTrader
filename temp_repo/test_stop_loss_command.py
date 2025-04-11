"""
Direct test script for the stop loss command with proper NLP flow
"""
import asyncio
import os
import sys
import re
from datetime import datetime

# Add the current directory to the path so we can import from discord_bot
sys.path.append('.')

# Import the Discord bot
from discord_bot import OptionsBot

def display_embed(embed, title_prefix=""):
    """Display a Discord embed in a formatted way for easy inspection"""
    print("\n" + "="*80)
    print(f"{title_prefix}")
    print("-"*80)
    
    # Display title and color
    try:
        color_hex = f"#{embed.color.value:06x}" if hasattr(embed, 'color') and hasattr(embed.color, 'value') else "None"
    except Exception:
        color_hex = str(embed.color) if hasattr(embed, 'color') else "None"
    
    print(f"Title: {embed.title}")
    print(f"Color: {color_hex}")
    print(f"Description: {embed.description}")
    
    # Display fields
    print("\nFIELDS:")
    for i, field in enumerate(embed.fields, 1):
        print(f"\n[{i}] {field.name}")
        print("-" * 40)
        
        # Look for buffer percentage indications in the field value
        buffer_match = re.search(r'(\d+\.\d+)% (?:below|above)', field.value)
        buffer_text = f"BUFFER: {buffer_match.group(1)}%" if buffer_match else ""
        
        # Also try to find the buffer in the debug logs
        debug_buffer = re.search(r'Buffer limit: \$[\d.]+\s+\((\d+\.\d+)%\)', field.value)
        if not buffer_match and debug_buffer:
            buffer_text = f"BUFFER LIMIT: {debug_buffer.group(1)}%"
        
        # Check for buffer limit messages
        if "maximum buffer limit" in field.value.lower():
            buffer_text += " ⚠️ MAXIMUM BUFFER APPLIED ⚠️"
        elif "buffer limit zone" in field.value.lower():
            buffer_text += " ⚠️ BUFFER LIMIT APPLIED ⚠️"
            
        # Check if this mentions technical level
        if "technical" in field.value.lower() and "support" in field.value.lower():
            buffer_text += " 📊 TECHNICAL SUPPORT LEVEL USED"
        elif "technical" in field.value.lower():
            buffer_text += " 📊 TECHNICAL LEVEL USED"
            
        # Add debug info about trade type
        trade_type_match = None
        if "scalp" in field.name.lower() or "scalp" in field.value.lower():
            trade_type_match = "SCALP (0-2 DTE)"
        elif "swing" in field.name.lower() or "swing" in field.value.lower():
            trade_type_match = "SWING (3-60 DTE)"
        elif "long" in field.name.lower() or "long" in field.value.lower():
            trade_type_match = "LONG-TERM (60+ DTE)"
            
        if trade_type_match:
            buffer_text += f" | Trade type: {trade_type_match}"
            
        print(field.value)
        if buffer_text:
            print(f"📊 {buffer_text}")
    
    # Display footer
    if embed.footer:
        print("\nFooter:", embed.footer.text)
    
    print("="*80)

async def test_stop_loss_query():
    try:
        print("Initializing bot...")
        bot = OptionsBot()
        print("Options bot initialized")
        
        # Comprehensive test of DTE-dependent buffer logic for both CALL and PUT options
        
        # Test all DTE ranges defined in the buffer limit requirements
        
        print("\n===== TEST 1: ULTRA-SHORT-TERM (0-1 DTE) =====")
        print("For 0-1 DTE, buffer should be 1.0%")
        tomorrow = "2025-04-09"  # 1 DTE from test date
        await test_option("SPY", 510, "call", tomorrow, bot)
        
        print("\n===== TEST 2: SHORT-TERM (2 DTE) =====") 
        print("For 2 DTE, buffer should be 2.0%")
        await test_option("QQQ", 410, "put", "2025-04-10", bot)
        
        print("\n===== TEST 3: MEDIUM-SHORT-TERM (3-5 DTE) =====")
        print("For 3-5 DTE, buffer should be 3.0%")
        await test_option("TSLA", 290, "call", "2025-04-11", bot)  # 3 DTE
        
        print("\n===== TEST 4: MEDIUM-TERM (6-60 DTE) =====")
        print("For 6-60 DTE, buffer should be 5.0%")
        await test_option("AAPL", 190, "put", "2025-05-02", bot)  # ~24 DTE
        
        print("\n===== TEST 5: LONG-TERM CALL (60+ DTE) =====")
        print("For 60+ DTE CALL options, buffer should be 5.0%")
        await test_option("MSFT", 400, "call", "2025-08-15", bot)  # >60 DTE
        
        print("\n===== TEST 6: LONG-TERM PUT (60+ DTE) =====")
        print("For 60+ DTE PUT options, buffer should be 7.0%")
        await test_option("SPY", 500, "put", "2025-08-15", bot)  # >60 DTE
        
    except Exception as e:
        print(f"Error in test_stop_loss_query: {e}")
        import traceback
        traceback.print_exc()

async def test_option(ticker, strike, option_type, expiration, bot):
    try:
        print(f"\n------- Testing {ticker} {option_type.upper()} with real query -------")
        print(f"Strike: ${strike}, Expiration: {expiration}")
        
        # Create a simple capturing class to record log output
        class LogCapture:
            def __init__(self):
                self.captured_logs = []
                
            def capture(self, content):
                if content:
                    self.captured_logs.append(content)
                
            def get_log_containing(self, substring):
                return [log for log in self.captured_logs if substring in log]
                
        log_capture = LogCapture()
                
        # Simulate a message
        class MockChannel:
            def __init__(self):
                self.name = "ai-options-calculator"  # Set to approved channel name
                self.type = type('obj', (object,), {'name': 'text'})

            async def send(self, content=None, embed=None):
                log_capture.capture(content)
                if embed:
                    display_embed(embed, f"{ticker} {option_type.upper()} Stop Loss Analysis:")
        
        class MockUser:
            def __init__(self):
                self.name = "TestUser"
                self.id = 12345
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
                self.channel = MockChannel()
                self.author = MockUser()
            
            async def reply(self, content=None, embed=None):
                log_capture.capture(content)
                if embed:
                    display_embed(embed, f"{ticker} {option_type.upper()} Stop Loss Analysis:")
                
        # Use the exact query format provided by the user
        query = f"<@1354551896605589584> stop loss reccomendation for my {ticker} {option_type.capitalize()}s with a strike price of {strike} and an expiration of {expiration}"
        
        message = MockMessage(query)
        
        # Create a custom print capture function that will be used for the bot's output
        import builtins
        orig_print = builtins.print
        
        # Define a custom print function
        def capturing_print(*args, **kwargs):
            # Get the original text
            content = " ".join(str(arg) for arg in args)
            # Capture the log
            log_capture.capture(content)
            # Call the original print
            return orig_print(*args, **kwargs)
            
        # Replace the built-in print function with our custom one
        builtins.print = capturing_print
        
        # Process the message through the handle_message method
        print(f"Sending query: {query}")
        response = await bot.handle_message(message)
        
        # Restore the original print function
        builtins.print = orig_print
        
        # Extract and validate the buffer logic
        buffer_logs = log_capture.get_log_containing("Buffer limit:")
        dte_logs = log_capture.get_log_containing("Days to expiration:")
        
        if buffer_logs and dte_logs:
            # Parse DTE
            dte_match = re.search(r'Days to expiration: (\d+)', dte_logs[0])
            dte = int(dte_match.group(1)) if dte_match else 0
            
            # Parse buffer percentage
            buffer_match = re.search(r'Buffer limit: \$[\d.]+ \(([\d.]+)%\)', buffer_logs[0])
            buffer_pct = float(buffer_match.group(1)) if buffer_match else 0
            
            # Validate buffer logic
            expected_buffer = 0.0
            if isinstance(dte, int):
                if dte <= 1:
                    expected_buffer = 1.0
                elif dte <= 2:
                    expected_buffer = 2.0
                elif dte <= 5:
                    expected_buffer = 3.0
                elif dte <= 60:
                    expected_buffer = 5.0
                else:
                    expected_buffer = 7.0 if option_type.lower() == 'put' else 5.0
                
            buffer_result = "✅ CORRECT" if abs(buffer_pct - expected_buffer) < 0.01 else "❌ INCORRECT"
            
            print(f"\n🧪 BUFFER VALIDATION RESULTS:")
            print(f"  DTE: {dte}")
            print(f"  Actual Buffer %: {buffer_pct}%")
            print(f"  Expected Buffer %: {expected_buffer}%")
            print(f"  Result: {buffer_result}")
        
        # Print the response
        print("Response type:", type(response))
        
        # If we got an embed back, display it in our formatted way
        if response and hasattr(response, 'fields'):
            display_embed(response, f"{ticker} {option_type.upper()} Stop Loss Response:")
        
    except Exception as e:
        print(f"Error in test_option: {e}")
        import traceback
        traceback.print_exc()

def main():
    # Run the async function
    asyncio.run(test_stop_loss_query())

if __name__ == "__main__":
    main()