import datetime
import discord
import yfinance as yf
import sys
import traceback

from discord_bot import OptionsBot

async def test_0dte_stop_loss():
    """Test the 0DTE fixed 15% stop loss logic"""
    
    print("====== TESTING 0DTE FIXED 15% STOP LOSS ======")
    
    # Create a mock message and channel for testing
    class MockChannel:
        async def send(self, content=None, embed=None):
            if embed:
                print(f"EMBED TITLE: {embed.title}")
                print(f"EMBED COLOR: {embed.color}")
                for field in embed.fields:
                    print(f"FIELD: {field.name}")
                    print(f"VALUE: {field.value}")
                    print("---")
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            if embed:
                print(f"REPLY EMBED TITLE: {embed.title}")
                print(f"REPLY EMBED COLOR: {embed.color}")
                for field in embed.fields:
                    print(f"FIELD: {field.name}")
                    print(f"VALUE: {field.value}")
                    print("---")
    
    # Initialize the options bot
    bot = OptionsBot()
    
    # Create test case for today's date (0DTE)
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Test SPY 0DTE call option
    call_message = MockMessage(f"@bot give me stop loss for SPY $490 calls expiring {today}")
    call_info = {
        'ticker': 'SPY',
        'strike': 490.0,
        'option_type': 'call',
        'expiration': today,
        'contract_count': 1
    }
    
    print("\n=== TESTING 0DTE CALL OPTION ===")
    try:
        call_result = await bot.handle_stop_loss_request(call_message, call_info)
        print("Successfully processed 0DTE call option request")
    except Exception as e:
        print(f"Error processing 0DTE call option: {e}")
        traceback.print_exc()
    
    # Test SPY 0DTE put option
    put_message = MockMessage(f"@bot give me stop loss for SPY $490 puts expiring {today}")
    put_info = {
        'ticker': 'SPY',
        'strike': 490.0,
        'option_type': 'put',
        'expiration': today,
        'contract_count': 1
    }
    
    print("\n=== TESTING 0DTE PUT OPTION ===")
    try:
        put_result = await bot.handle_stop_loss_request(put_message, put_info)
        print("Successfully processed 0DTE put option request")
    except Exception as e:
        print(f"Error processing 0DTE put option: {e}")
        traceback.print_exc()

# Run the test
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_0dte_stop_loss())
