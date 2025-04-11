"""
This script tests the specific case of a TSLA stop loss query that was causing issues.
It focuses on testing the Discord mention ID fix and the price extraction logic.
"""

import asyncio
from discord_bot import OptionsBotNLP, OptionsBot

async def test_tsla_stop_loss():
    """Test a specific TSLA stop loss request with mention"""
    print("\n=== Testing TSLA Stop Loss with Discord Mention ===")
    
    # Create instances of our NLP and bot classes
    nlp = OptionsBotNLP()
    bot = OptionsBot()
    
    # This is the specific test query that was causing issues
    test_query = "<@1354551896605589584> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    
    print(f"Test query: {test_query}")
    
    # Parse the query with our NLP processor
    request_type, info = nlp.parse_query(test_query)
    
    print(f"\nParse Results:")
    print(f"Request Type: {request_type}")
    print(f"Info extracted:")
    for key, value in info.items():
        if value is not None:  # Only print non-None values
            print(f"  {key}: {value}")
    
    # Verify we got the expected results
    expected_values = {
        "ticker": "TSLA",
        "strike": 270.0,
        "option_type": "call",
        "expiration": "2025-04-04",
    }
    
    all_correct = True
    for key, expected in expected_values.items():
        if key in info and info[key] == expected:
            print(f"✅ {key} correctly extracted as {expected}")
        else:
            print(f"❌ {key} incorrectly extracted as {info.get(key)}, expected {expected}")
            all_correct = False
    
    # Make sure the price isn't the huge Discord ID number
    if 'price' in info and info['price'] == 270.0:
        print("✅ Price correctly extracted as 270.0")
    elif 'price' in info and info['price'] < 10000:  # Some reasonable price, not a huge ID
        print(f"✅ Price reasonably extracted as {info['price']}")
    elif 'price' in info and info['price'] > 1000000000:  # A huge number like a Discord ID
        print(f"❌ Price is an unreasonable value: {info['price']}, likely a Discord ID")
        all_correct = False
    
    # Overall result
    if all_correct:
        print("\n🎉 All values were correctly extracted! The fix is working properly.")
    else:
        print("\n❌ Some values were not correctly extracted. The fix may not be working completely.")
    
    print("\nNow testing the actual bot response generation:")
    
    # Set up a mock message class that we can use to test the bot's handle_message method
    class MockChannel:
        async def send(self, content=None, embed=None):
            if content:
                print(f"Channel message: {content}")
            if embed:
                print(f"Embed title: {embed.title}")
                print(f"Embed description: {embed.description}")

    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.channel = MockChannel()
            self.author = type('obj', (object,), {
                'mention': 'TestUser',
                'name': 'TestUser',
                'id': 12345
            })
            
        async def reply(self, content=None, embed=None):
            if content:
                print(f"Reply message: {content}")
            if embed:
                print(f"Reply embed title: {embed.title}")
                print(f"Reply embed description: {embed.description[:100]}..." if embed.description else "No description")
    
    # Create a mock message with our test query
    mock_message = MockMessage(test_query)
    
    try:
        # Call the bot's handle_message method with our mock message
        await bot.handle_message(mock_message)
        print("\n✅ Bot was able to handle the message without errors")
    except Exception as e:
        print(f"\n❌ Bot encountered an error: {str(e)}")
    
    print("\nTest complete!")

async def main():
    await test_tsla_stop_loss()

if __name__ == "__main__":
    asyncio.run(main())