"""
Final test of the buffer enforcement code
"""
import asyncio
import sys
import os
import datetime

sys.path.append('.')

from discord_bot import OptionsBot


async def test_buffer_enforcement():
    try:
        # Initialize the bot
        print("Initializing bot...")
        options_bot = OptionsBot()
        print("Options bot initialized")
        
        # Define test cases
        test_cases = [
            {
                "name": "SPY CALL 1DTE (Buffer limit: 1.0%)",
                "ticker": "SPY",
                "strike": 500,
                "option_type": "call",
                "expiration": "2025-04-09",  # 1 day out
            },
            {
                "name": "SPY PUT 1DTE (Buffer limit: 1.0%)",
                "ticker": "SPY",
                "strike": 490,
                "option_type": "put",
                "expiration": "2025-04-09",  # 1 day out
            },
            {
                "name": "TSLA CALL 24DTE (Buffer limit: 5.0%)",
                "ticker": "TSLA",
                "strike": 270, 
                "option_type": "call",
                "expiration": "2025-05-02",  # 24 days out
            },
            {
                "name": "AAPL PUT 60+DTE (Buffer limit: 7.0%)",
                "ticker": "AAPL",
                "strike": 170,
                "option_type": "put",
                "expiration": "2025-07-18",  # ~100 days out
            }
        ]
        
        # Create mock message and channel classes
        class MockChannel:
            async def send(self, content=None, embed=None):
                if content:
                    print(f"Channel would receive: {content}")
                if embed:
                    print(f"\nEmbed title: {embed.title}")
                    for field in embed.fields:
                        print(f"\n{field.name}")
                        print(f"{field.value}")
        
        class MockMessage:
            def __init__(self, content, test_case):
                self.content = content
                self.channel = MockChannel()
                self.author = MockUser()
                self.test_case = test_case
            
            async def reply(self, content=None, embed=None):
                print(f"\n----- RESULTS FOR {self.test_case['name']} -----")
                if content:
                    print(f"Reply: {content}")
                if embed:
                    print(f"Embed title: {embed.title}")
                    for field in embed.fields:
                        print(f"\n{field.name}")
                        print(f"{field.value}")
        
        class MockUser:
            def __init__(self):
                self.name = "TestUser"
                self.id = 12345
        
        # Process each test case
        for case in test_cases:
            # Create the query and message
            query = f"@SWJ Options AI-Calculator What's the stop loss for {case['ticker']} ${case['strike']} {case['option_type']} expiring {case['expiration']}?"
            
            message = MockMessage(query, case)
            
            print(f"\n\n===== TESTING {case['name']} =====")
            print(f"Query: {query}")
            
            # Process the message
            await options_bot.handle_stop_loss_request(message, {
                'intent': 'stop_loss',
                'ticker': case['ticker'],
                'strike_price': case['strike'],
                'option_type': case['option_type'],
                'expiration_date': case['expiration']
            })
            
            print("\n")
        
    except Exception as e:
        print(f"Error in test_buffer_enforcement: {e}")
        import traceback
        traceback.print_exc()

def main():
    # Run the async function
    asyncio.run(test_buffer_enforcement())

if __name__ == "__main__":
    main()