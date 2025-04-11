"""
Test script to debug the specific TSLA stop loss query issue
"""
import asyncio
import os
import json
from datetime import datetime
import traceback

from discord_bot import OptionsBot, OptionsBotNLP

def test_message_parsing():
    """Test the NLP parsing of the query"""
    print("\n===== TESTING NLP PARSING =====")
    nlp = OptionsBotNLP()
    
    query = "Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    print(f"Query: {query}")
    
    # Parse the query
    result = nlp.parse_query(query)
    # The parse_query method returns a tuple (request_type, info_dict)
    request_type, info = result
    
    print("\nParsed Information:")
    print(f"Request Type: {request_type}")
    print(json.dumps(info, indent=2))
    
    # Check extraction
    if request_type != 'stop_loss':
        print(f"⚠️ Request type not correctly identified: {request_type}")
    
    if info.get('ticker') != 'TSLA':
        print(f"⚠️ Ticker not correctly extracted: {info.get('ticker')}")
    
    if info.get('strike') != 270.0:
        print(f"⚠️ Strike price not correctly extracted: {info.get('strike')}")
    
    if info.get('option_type') != 'call':
        print(f"⚠️ Option type not correctly extracted: {info.get('option_type')}")
    
    if info.get('expiration') != '2025-04-04':
        print(f"⚠️ Expiration date not correctly extracted: {info.get('expiration')}")
    
    # CRITICAL ERROR: The NLP is incorrectly setting target_price to 4.0
    if info.get('target_price') == 4.0:
        print(f"⚠️ ERROR: Target price incorrectly set to {info.get('target_price')} from the expiration date")
        # This is causing the Yahoo Finance 404 error when it tries to use this as a ticker symbol
        print("This is causing a 404 error when option_calculator.py tries to use this value as a ticker")
    
    print("========================================")
    return result

def test_mention_handling():
    """Test how the mention is handled in the query"""
    print("\n===== TESTING MENTION HANDLING =====")
    nlp = OptionsBotNLP()
    
    query = "<@1354551896605589584> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    print(f"Query with mention: {query}")
    
    # First, we need to clean the mention
    cleaned_query = query.replace("<@1354551896605589584>", "").strip()
    print(f"Cleaned query: {cleaned_query}")
    
    # Parse the cleaned query
    result = nlp.parse_query(cleaned_query)
    request_type, info = result
    
    print("\nParsed Information after mention removal:")
    print(f"Request Type: {request_type}")
    print(json.dumps(info, indent=2))
    
    print("========================================")
    return result

async def test_stop_loss_handling():
    """Test the full stop loss request handling"""
    print("\n===== TESTING FULL STOP LOSS HANDLING =====")
    bot = OptionsBot()
    
    # Create a mock message class with mentioning the bot
    class MockChannel:
        async def send(self, content):
            print(f"Channel message: {content}")
            return MockMessage(content)
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            if content:
                print(f"Reply content: {content}")
            if embed:
                print(f"Reply embed title: {embed.title}")
                print(f"Reply embed description: {embed.description[:100]}..." if embed.description else "No description")
            return MockMessage("Reply message")
    
    # Create the mock message
    mock_message = MockMessage("<@1354551896605589584> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025")
    
    try:
        # Call the main message handler
        await bot.handle_message(mock_message)
    except Exception as e:
        print(f"Error in handle_message: {str(e)}")
        print(traceback.format_exc())
    
    print("========================================")

def test_direct_stop_loss_request():
    """Test directly calling the stop loss request with the parsed info"""
    print("\n===== TESTING DIRECT STOP LOSS REQUEST =====")
    
    # Create an instance of the bot
    bot = OptionsBot()
    
    # Create a mock message
    class MockChannel:
        async def send(self, content):
            print(f"Channel message: {content}")
            return MockMessage(content)
    
    class MockMessage:
        def __init__(self, content):
            self.content = "Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            if content:
                print(f"Reply content: {content}")
            if embed:
                print(f"Reply embed title: {embed.title}")
                print(f"Reply embed description: {embed.description[:100]}..." if embed.description else "No description")
            return MockMessage("Reply message")
    
    # Initialize with known good values - based on debug_tsla_stop_loss.py
    # Note: Not including target_price as it was causing the 404 error
    test_info = {
        'ticker': 'TSLA',
        'strike': 270.0,
        'option_type': 'call',
        'expiration': '2025-04-04',
        'contract_count': 1
    }
    
    try:
        # Call the stop loss function directly
        response = asyncio.run(bot.handle_stop_loss_request(
            message=MockMessage("test"),
            info=test_info
        ))
        
        # Check the response
        if hasattr(response, 'title'):
            print(f"Response title: {response.title}")
        if hasattr(response, 'description'):
            print(f"Response description snippet: {response.description[:200]}...")
        else:
            print(f"Response type: {type(response)}")
            print(f"Response content: {response}")
    except Exception as e:
        print(f"Error in direct stop loss request: {str(e)}")
        print(traceback.format_exc())
    
    print("========================================")

def main():
    """Main test function that runs all the tests"""
    # Test the NLP parsing
    info = test_message_parsing()
    
    # Test mention handling
    mention_info = test_mention_handling()
    
    # Test direct stop loss request
    test_direct_stop_loss_request()
    
    # Test the full stop loss handling
    asyncio.run(test_stop_loss_handling())

if __name__ == "__main__":
    main()