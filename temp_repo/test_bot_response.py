"""
Test script to directly test the Discord bot's functionality
"""

import asyncio
import discord
from discord_bot import OptionsBot, OptionsBotNLP

async def test_bot():
    print("Initializing test bot...")
    bot = OptionsBot()
    nlp = OptionsBotNLP()
    
    # Mock message class
    class MockMessage:
        def __init__(self, content, author=None):
            self.content = content
            self.author = author or MockUser()
            self.mentions = []
            self.channel = MockChannel()
            
        async def reply(self, content=None, embed=None):
            print(f"Reply sent: {content}")
            if embed:
                print(f"Embed title: {embed.title}")
                print(f"Embed description: {embed.description}")
                for field in embed.fields:
                    print(f"Field: {field.name} - {field.value}")
    
    class MockUser:
        def __init__(self):
            self.id = 12345
            self.bot = False
            self.name = "TestUser"
    
    class MockChannel:
        def __init__(self):
            self.id = 67890
            self.name = "blank1"  # Use the channel name that the bot is restricted to
            
        async def send(self, content=None, embed=None):
            print(f"Message sent to channel: {content}")
            if embed:
                print(f"Embed title: {embed.title}")
                print(f"Embed description: {embed.description}")
                for field in embed.fields:
                    print(f"Field: {field.name} - {field.value}")
    
    # Test queries
    test_queries = [
        "how do i interact with you"
    ]
    
    # Processing each test query
    for query in test_queries:
        print("\n" + "="*50)
        print(f"Testing query: {query}")
        print("="*50)
        
        # Create a mock message
        bot_mention = MockUser()
        bot_mention.id = 1354551896605589584  # Actual bot ID from logs
        bot_mention.name = "SWJ Options AI-Calculator"
        
        mock_msg = MockMessage(f"<@1354551896605589584> {query}")
        mock_msg.mentions = [bot_mention]
        
        try:
            # Process the message directly
            info = nlp.parse_query(query)
            print(f"Query parsed as: {info['request_type']} request")
            print(f"Extracted info: {info}")
            
            # Handle the message
            response = await bot.handle_message(mock_msg)
            if response:
                print("\nFull Response Embed:")
                print(f"Title: {response.title}")
                print(f"Description: {response.description}")
                for field in response.fields:
                    print(f"Field: {field.name} - {field.value}")
            
        except Exception as e:
            print(f"Error processing query: {e}")
            import traceback
            traceback.print_exc()
        
        # Wait a bit between tests
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_bot())