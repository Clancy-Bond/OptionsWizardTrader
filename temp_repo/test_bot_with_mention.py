"""
Test script to simulate the bot handling a specific query
"""
import asyncio
from discord_bot import OptionsBot

async def test_query():
    # Create the bot instance
    bot = OptionsBot()
    
    class MockChannel:
        async def send(self, content=None, embed=None):
            print("SENT TO CHANNEL:")
            if content:
                print(f"Content: {content}")
            if embed:
                if hasattr(embed, 'to_dict'):
                    embed_dict = embed.to_dict()
                    print(f"Embed Title: {embed_dict.get('title', 'No title')}")
                    print(f"Embed Description: {embed_dict.get('description', 'No description')}")
                    if 'fields' in embed_dict:
                        for field in embed_dict['fields']:
                            print(f"Field {field.get('name')}: {field.get('value')}")
                else:
                    print(f"Embed Title: {getattr(embed, 'title', 'No title')}")
                    print(f"Embed Description: {getattr(embed, 'description', 'No description')}")
            print("-" * 50)
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.channel = MockChannel()
            self.mentions = [MockUser()]  # Simulate that the bot is mentioned
            self.author = MockUser(id=12345)  # Different ID than the bot
            
        async def reply(self, content=None, embed=None):
            print("REPLY TO MESSAGE:")
            if content:
                print(f"Content: {content}")
            if embed:
                if hasattr(embed, 'to_dict'):
                    embed_dict = embed.to_dict()
                    print(f"Embed Title: {embed_dict.get('title', 'No title')}")
                    print(f"Embed Description: {embed_dict.get('description', 'No description')}")
                    if 'fields' in embed_dict:
                        for field in embed_dict['fields']:
                            print(f"Field {field.get('name')}: {field.get('value')}")
                else:
                    print(f"Embed Title: {getattr(embed, 'title', 'No title')}")
                    print(f"Embed Description: {getattr(embed, 'description', 'No description')}")
            print("-" * 50)
    
    class MockUser:
        def __init__(self, id=1354551896605589584):  # Use the bot's ID by default
            self.id = id
            self.mention = f"<@{id}>"
            self.bot = False  # Not a bot user
    
    # Create a mock message
    message = MockMessage("<@1354551896605589584> Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025")
    
    # Print the message content before processing
    print(f"Testing with message: {message.content}")
    print("-" * 50)
    
    # Log steps of the process with detailed error handling
    try:
        print("STEP 1: NLP Parsing")
        nlp = bot.nlp
        result = nlp.parse_query(message.content)
        print(f"NLP Result: {result}")
        print("-" * 50)
        
        print("STEP 2: Bot message handling")
        await bot.handle_message(message)
    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())

def main():
    asyncio.run(test_query())

if __name__ == "__main__":
    main()