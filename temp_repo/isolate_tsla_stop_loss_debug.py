"""
Simplified and targeted debug script for the TSLA stop loss issue
This script will isolate just the handle_stop_loss_request function and trace its execution
"""
import asyncio
import traceback
import sys
import inspect
from datetime import datetime, date

# Mock classes for testing
class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
    
    async def reply(self, content=None, embed=None):
        print(f"REPLY: {content if content else 'Embed: ' + getattr(embed, 'title', 'No title')}")

class MockUser:
    def __init__(self):
        self.id = 123456789
        self.name = "TestUser"

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

# Import necessary components
from discord_bot import OptionsBot
from technical_analysis import get_stop_loss_recommendation
from option_calculator import calculate_option_at_stop_loss, calculate_theta_decay, calculate_expiry_theta_decay

async def debug_tsla_stop_loss():
    print("===== DEBUGGING TSLA STOP LOSS ISSUE =====")
    
    # Create test info and message
    info = {
        'ticker': 'TSLA',
        'strike': 270.0,
        'option_type': 'call',
        'expiration': '2025-04-04',
        'contract_count': 1
    }
    
    message = MockMessage(f"<@123456789> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025")
    
    # Create bot instance
    bot = OptionsBot()
    
    # Add debug prints to track flow and variables
    original_method = bot.handle_stop_loss_request
    
    async def debug_wrapper(self, message, info):
        """Debug wrapper to trace execution"""
        print(f"\n==== ENTERING handle_stop_loss_request ====")
        print(f"Message: {message.content}")
        print(f"Info: {info}")
        
        # Calculate days to expiration
        if 'expiration' in info and info['expiration']:
            expiry_date = datetime.strptime(info['expiration'], "%Y-%m-%d").date()
            today = date.today()
            days_to_expiration = (expiry_date - today).days
            print(f"Days to expiration: {days_to_expiration}")
        
        # Call the original method
        try:
            print("Calling original method...")
            # Original method is already bound to the bot instance, so we don't pass self
            result = await original_method(message, info)
            
            print(f"\n==== ORIGINAL METHOD RETURNED ====")
            print(f"Result type: {type(result)}")
            
            if result is None:
                print("WARNING: Original method returned None")
            elif hasattr(result, 'title'):
                print(f"Result title: {result.title}")
                print(f"Result description sample: {result.description[:100]}...")
                
                if hasattr(result, '_fields') and result._fields:
                    print(f"Fields: {len(result._fields)}")
                    for field in result._fields:
                        print(f"  - {field.get('name', 'No name')}")
            
            return result
        except Exception as e:
            print(f"EXCEPTION IN ORIGINAL METHOD: {str(e)}")
            traceback.print_exc(file=sys.stdout)
            return None
    
    # Replace the original method with our debug wrapper
    bot.handle_stop_loss_request = debug_wrapper.__get__(bot, OptionsBot)
    
    # Call the method
    try:
        result = await bot.handle_stop_loss_request(message, info)
        
        print("\n==== FINAL RESULT ====")
        if result is None:
            print("Final result is None - this indicates a bug in handle_stop_loss_request")
        else:
            print(f"Final result title: {getattr(result, 'title', 'No title')}")
            if hasattr(result, 'description'):
                print(f"Description sample: {result.description[:100]}...")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    asyncio.run(debug_tsla_stop_loss())