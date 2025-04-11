"""
Debugging script to isolate and test the specific SPY 1DTE query
"""
import asyncio
import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import from discord_bot
sys.path.append('.')

# Import the Discord bot
from discord_bot import OptionsBotNLP


async def test_stop_loss_query():
    try:
        print("Initializing bot...")
        nlp_bot = OptionsBotNLP()
        print("NLP bot initialized")
        
        # We'll use the NLP bot that's already initialized
        bot = nlp_bot
        print("Using NLP bot for tests")
        
        # Test the specific TSLA query with realistic parameters
        print("\n------- Testing TSLA CALL with real query -------")
        ticker = "TSLA"
        strike = 290
        option_type = "call"
        expiration = "2025-05-02"  # 24 days out
        
        # Simulate a message
        class MockChannel:
            async def send(self, content=None, embed=None):
                print(f"Channel would receive: {content}")
                if embed:
                    print(f"Embed title: {embed.title}")
                    for field in embed.fields:
                        print(f"Field: {field.name}")
                        print(f"Value: {field.value}")
                        print("")
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
                self.channel = MockChannel()
                self.author = MockUser()
            
            async def reply(self, content=None, embed=None):
                print(f"Reply would be: {content}")
                if embed:
                    print(f"Embed title: {embed.title}")
                    for field in embed.fields:
                        print(f"Field: {field.name}")
                        print(f"Value: {field.value}")
                        print("")
        
        class MockUser:
            def __init__(self):
                self.name = "TestUser"
                self.id = 12345
                
        # Use the exact query format provided by the user
        query = f"<@1354551896605589584> stop loss reccomendation for my {ticker} {option_type.capitalize()}s with a strike price of {strike} and an expiration of {expiration}"
        
        message = MockMessage(query)
        
        # Process the message
        print(f"Sending query: {query}")
        await bot.handle_stop_loss_request(message, {
            'intent': 'stop_loss',
            'ticker': ticker,
            'strike_price': strike,
            'option_type': option_type,
            'expiration_date': expiration
        })
        
        # Test the TSLA query (previous error case)
        print("\n------- Testing TSLA 24DTE CALL -------")
        ticker = "TSLA"
        strike = 270
        option_type = "call"
        expiration = "2025-05-02"  # 24 days out
        
        # Use the exact query format provided by the user
        query = f"<@1354551896605589584> stop loss reccomendation for my {ticker} {option_type.capitalize()}s with a strike price of {strike} and an expiration of {expiration}"
        
        message = MockMessage(query)
        
        # Process the message
        print(f"Sending query: {query}")
        await bot.handle_stop_loss_request(message, {
            'intent': 'stop_loss',
            'ticker': ticker,
            'strike_price': strike,
            'option_type': option_type,
            'expiration_date': expiration
        })
        
        # Test PUT option
        print("\n------- Testing SPY 1DTE PUT -------")
        ticker = "SPY"
        strike = 490
        option_type = "put"
        expiration = "2025-04-09"  # 1 day out
        
        # Use the exact query format provided by the user
        query = f"<@1354551896605589584> stop loss reccomendation for my {ticker} {option_type.capitalize()}s with a strike price of {strike} and an expiration of {expiration}"
        
        message = MockMessage(query)
        
        # Process the message
        print(f"Sending query: {query}")
        await bot.handle_stop_loss_request(message, {
            'intent': 'stop_loss',
            'ticker': ticker,
            'strike_price': strike,
            'option_type': option_type,
            'expiration_date': expiration
        })
        
    except Exception as e:
        print(f"Error in test_stop_loss_query: {e}")
        import traceback
        traceback.print_exc()

def main():
    # Run the async function
    asyncio.run(test_stop_loss_query())

if __name__ == "__main__":
    main()