"""
This script adds a fix to test both our handle_message method and the parse_query method
to identify the specific issue with the TSLA stop loss query.
"""

import asyncio
import traceback
import sys
from discord_bot import OptionsBot, OptionsBotNLP

async def test_integrated_parsing_and_handling():
    """Test both parsing and handling in a combined workflow"""
    print("\n========== TESTING INTEGRATED PARSING AND HANDLING ==========")
    
    # Create objects
    nlp = OptionsBotNLP()
    bot = OptionsBot()
    
    # Set up the mock message class
    class MockChannel:
        async def send(self, content=None, embed=None):
            print("Channel.send() called")
            if content:
                print(f"Content: {content[:100]}...")  # First 100 chars
            if embed:
                print(f"Embed title: {getattr(embed, 'title', 'No title')}")
                embed_desc = getattr(embed, 'description', 'No description')
                print(f"Embed description: {embed_desc[:min(len(embed_desc), 100)]}...")  # First 100 chars
    
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
                embed_desc = getattr(embed, 'description', 'No description')
                print(f"Embed description: {embed_desc[:min(len(embed_desc), 100)]}...")  # First 100 chars
    
    # Test query
    query = "<@1354551896605589584> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    
    # PART 1: Manual steps - Parse the query directly with NLP
    print("\nPART 1: Manually parse the query with NLP")
    try:
        # Parse the query to get request_type and info
        request_type, info = nlp.parse_query(query)
        print(f"Parse query returned: request_type={request_type}, info={info}")
        
        # Check if info is a dictionary or tuple
        print(f"Type of info: {type(info)}")
        
        # Ensure request_type and info are correct types
        assert isinstance(request_type, str), "request_type should be a string"
        assert isinstance(info, dict), "info should be a dictionary"
        
        # Check for required fields in info
        required_fields = ['ticker', 'option_type', 'strike', 'expiration']
        for field in required_fields:
            assert field in info, f"Required field '{field}' missing from info"
            print(f"Required field '{field}' present: {info[field]}")
    except Exception as e:
        print(f"ERROR in manual parsing: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    
    # PART 2: Integrated test - Handle the message which will call parse_query internally
    print("\nPART 2: Integrated test with handle_message")
    try:
        # Create a mock message with the query
        message = MockMessage(query)
        
        # Call handle_message
        embed = await bot.handle_message(message)
        print(f"handle_message returned: {type(embed)}")
    except Exception as e:
        print(f"ERROR in integrated test: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    
    # PART 3: Test handle_stop_loss_request directly with known good info
    print("\nPART 3: Testing handle_stop_loss_request directly")
    try:
        # Create info with the known good format
        good_info = {
            'ticker': 'TSLA',
            'option_type': 'call',
            'strike': 270.0,
            'expiration': '2025-04-04',
            'contract_count': 1,
            'target_price': None,
            'move_amount': None,
            'move_direction': None,
            'target_date': None
        }
        
        # Call handle_stop_loss_request directly
        message = MockMessage(query)
        embed = await bot.handle_stop_loss_request(message, good_info)
        print(f"handle_stop_loss_request returned: {type(embed)}")
    except Exception as e:
        print(f"ERROR in direct stop loss test: {str(e)}")
        traceback.print_exc(file=sys.stdout)

# Main entry point
if __name__ == "__main__":
    asyncio.run(test_integrated_parsing_and_handling())