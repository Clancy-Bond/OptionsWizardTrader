"""
Test script to debug the specific query: '@OptionsBot Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025'
This script will simulate the Discord bot receiving this message and trace the execution.
"""

import sys
import traceback
from discord_bot import OptionsBotNLP, OptionsBot

# Test the NLP parsing
def test_nlp_parsing():
    print("TEST 1: Testing NLP parsing...")
    nlp = OptionsBotNLP()
    
    query = "Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    print(f"Query: {query}")
    
    try:
        result = nlp.parse_query(query)
        print(f"Parsed info: {result}")
        
        # The NLP parse_query returns a tuple (request_type, info_dict)
        if isinstance(result, tuple) and len(result) == 2:
            request_type, info = result
            print(f"Request Type: {request_type}")
            
            # Check for expected keys in the info dictionary
            expected_keys = ['ticker', 'strike', 'option_type', 'expiration']
            missing_keys = [key for key in expected_keys if key not in info]
            
            if missing_keys:
                print(f"ERROR: Missing expected keys in info dict: {missing_keys}")
            else:
                print("All expected keys are present in the info dictionary")
                
            # Print detailed parsing results
            print(f"Ticker: {info.get('ticker')}")
            print(f"Strike Price: {info.get('strike')}")
            print(f"Option Type: {info.get('option_type')}")
            print(f"Expiration: {info.get('expiration')}")
        else:
            print("ERROR: Expected a tuple (request_type, info_dict) but got something else")
    
    except Exception as e:
        print(f"ERROR in NLP parsing: {str(e)}")
        traceback.print_exc()

# Test the bot's handling of the query
async def test_bot_handling():
    print("\nTEST 2: Testing bot handling...")
    bot = OptionsBot()
    
    # Create a mock message class
    class MockChannel:
        async def send(self, content=None, embed=None):
            print("Channel.send() called")
            if content:
                print(f"Content: {content[:100]}...")  # First 100 chars
            if embed:
                print(f"Embed title: {getattr(embed, 'title', 'No title')}")
                print(f"Embed description: {getattr(embed, 'description', 'No description')[:100]}...")  # First 100 chars

    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.channel = MockChannel()
            self.author = type('obj', (object,), {'id': 12345, 'mention': '@user'})
            self.mentions = [type('obj', (object,), {'id': 1354551896605589584, 'name': 'OptionsBot'})]
        
        async def reply(self, content=None, embed=None):
            print("Message.reply() called")
            if content:
                print(f"Reply content: {content[:100]}...")  # First 100 chars
            if embed:
                print(f"Embed title: {getattr(embed, 'title', 'No title')}")
                print(f"Embed description: {getattr(embed, 'description', 'No description')[:100]}...")  # First 100 chars
    
    # Create a mock message with the query
    message = MockMessage("<@1354551896605589584> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025")
    
    try:
        print("Calling bot.handle_message...")
        result = await bot.handle_message(message)
        print(f"Result from handle_message: {result}")
    except Exception as e:
        print(f"ERROR in bot handling: {str(e)}")
        traceback.print_exc(file=sys.stdout)

# Test the specific stop loss request handling directly
async def test_direct_stop_loss():
    print("\nTEST 3: Testing direct stop loss handling...")
    bot = OptionsBot()
    
    # Create a mock message class
    class MockChannel:
        async def send(self, content=None, embed=None):
            print("Channel.send() called")
            if content:
                print(f"Content: {content[:100]}...")  # First 100 chars
            if embed:
                print(f"Embed title: {getattr(embed, 'title', 'No title')}")
                print(f"Embed description: {getattr(embed, 'description', 'No description')[:100]}...")  # First 100 chars

    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.channel = MockChannel()
            self.author = type('obj', (object,), {'id': 12345, 'mention': '@user'})
        
        async def reply(self, content=None, embed=None):
            print("Message.reply() called")
            if content:
                print(f"Reply content: {content[:100]}...")  # First 100 chars
            if embed:
                print(f"Embed title: {getattr(embed, 'title', 'No title')}")
                print(f"Embed description: {getattr(embed, 'description', 'No description')[:100]}...")  # First 100 chars
    
    # Create info dict similar to what would be parsed from the query
    # Note: The handle_stop_loss_request expects just the info dict, not including request_type
    info = {
        'ticker': 'TSLA',
        'strike': 270.0,
        'option_type': 'call',
        'expiration': '2025-04-04',  # Format expected by the bot
        'contract_count': 1          # Default to 1 contract
    }
    
    # Mock message
    message = MockMessage("Test message")
    
    try:
        await bot.handle_stop_loss_request(message, info)
    except Exception as e:
        print(f"ERROR in direct stop loss handling: {str(e)}")
        traceback.print_exc()

# Main function to run all tests
def main():
    print("======== TESTING BOT RESPONSE TO TSLA STOP LOSS QUERY ========")
    
    # Test NLP parsing
    test_nlp_parsing()
    
    # Use asyncio to run the async tests
    import asyncio
    
    # Run the bot handling test
    print("\nRunning async bot handling test...")
    asyncio.run(test_bot_handling())
    
    # Run the direct stop loss test
    print("\nRunning async direct stop loss test...")
    asyncio.run(test_direct_stop_loss())

if __name__ == "__main__":
    main()