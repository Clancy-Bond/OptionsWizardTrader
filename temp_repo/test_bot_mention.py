"""
Test script to directly verify the bot's mention detection.
This simulates a Discord message with a mention and verifies the bot can process it.
"""
import asyncio
import os
from dotenv import load_dotenv
import discord

load_dotenv()  # Load environment variables

# Create mock objects to simulate Discord
class MockUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.display_name = name
        self.mention = f"<@{id}>"

class MockChannel:
    def __init__(self, name):
        self.name = name
        
    async def send(self, content=None, embed=None):
        print(f"[MOCK] Channel.send called with content: {content}")
        if embed:
            print(f"[MOCK] Embed title: {embed.title}")
            print(f"[MOCK] Embed description: {embed.description}")
        return "Message sent successfully"

class MockGuild:
    def __init__(self):
        self.name = "Test Guild"
    
    def get_member(self, id):
        return MockUser(id, f"User_{id}")

class MockMessage:
    def __init__(self, content, author=None, channel=None):
        self.content = content
        self.author = author or MockUser(123456789, "TestUser")
        self.channel = channel or MockChannel("bot-testing")
        self.guild = MockGuild()
        
    async def reply(self, content=None, embed=None):
        print(f"[MOCK] Message.reply called with content: {content}")
        if embed:
            print(f"[MOCK] Embed title: {embed.title}")
            print(f"[MOCK] Embed description: {embed.description}")
        return "Reply sent successfully"

# Import the bot from discord_bot.py
from discord_bot import OptionsBot

async def test_mention_detection():
    """Test if the bot can correctly detect and respond to mentions"""
    bot = OptionsBot()
    
    # Get bot user ID from env
    bot_user_id = os.getenv('BOT_USER_ID')
    if not bot_user_id:
        print("ERROR: BOT_USER_ID not found in environment variables!")
        return
    
    print(f"Testing with bot ID: {bot_user_id}")
    
    # Test different mention formats
    test_messages = [
        f"<@{bot_user_id}> what's a good stop loss for AAPL $200 calls expiring next Friday?",
        f"<@{bot_user_id}> show me unusual options activity for MSFT",
        f"<@{bot_user_id}> what's the price of AAPL $180 calls expiring Apr 12th?"
    ]
    
    for idx, message_content in enumerate(test_messages):
        print(f"\n----- Test {idx+1}: {message_content} -----")
        
        # Create mock message
        mock_message = MockMessage(message_content)
        
        # Process the message
        response = await bot.handle_message(mock_message)
        
        if response:
            print("✅ Bot generated a response!")
            if isinstance(response, discord.Embed):
                print(f"Response type: Embed")
                print(f"Title: {response.title}")
                print(f"Description: {response.description[:100]}...")
            else:
                print(f"Response type: {type(response)}")
                print(f"Response: {str(response)[:100]}...")
        else:
            print("❌ Bot did not generate a response!")

async def main():
    await test_mention_detection()

if __name__ == "__main__":
    asyncio.run(main())