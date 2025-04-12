"""
Quick test for the Discord bot's unusual options activity command
"""
import asyncio
from discord_bot import OptionsBot

async def test_unusual_activity():
    """
    Test the unusual options activity command via the Discord bot interface
    """
    # Create a mock message object to pass to the bot
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.author = type('obj', (object,), {'id': 123456})
            self.channel = type('obj', (object,), {'id': 789012})
            
        async def reply(self, content):
            print("\n*** BOT RESPONSE ***")
            print(content)
            print("*******************\n")
    
    # Create bot and initialize it
    bot = OptionsBot()
    await bot.on_ready()
    
    # Test the unusual options activity request for TSLA
    message = MockMessage("@bot show me unusual options activity for TSLA")
    await bot.on_message(message)
    
    # Give some time for the async process to complete
    await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(test_unusual_activity())