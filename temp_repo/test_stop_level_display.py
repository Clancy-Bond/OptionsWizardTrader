"""
Test script to verify that the stop level percentage changes are correctly displayed
in Discord bot responses.
"""
import asyncio
import discord
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Test message to check the updated stop level percentage display
TEST_QUERY = "What's a good stop loss for AAPL $180 calls expiring next Friday?"

class TestClient(discord.Client):
    """Simple client to test the bot's response formatting"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_complete = False
    
    async def on_ready(self):
        """When the bot is ready, send a test message"""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
        # Find the test channel - using your channel name
        test_channel = None
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.name == "blank1":  # Replace with your actual test channel name
                    test_channel = channel
                    break
            if test_channel:
                break
        
        if not test_channel:
            print("Couldn't find test channel. Please set up a channel named 'blank1'")
            await self.close()
            return
        
        # Find the bot user to mention
        bot_user = None
        for guild in self.guilds:
            for member in guild.members:
                if member.bot and "SWJ" in member.name and "Options" in member.name:
                    bot_user = member
                    break
            if bot_user:
                break
        
        if bot_user:
            # Send the test message with a proper mention
            print(f"Found bot user: {bot_user.name}, sending test message")
            await test_channel.send(f"<@{bot_user.id}> {TEST_QUERY}")
        else:
            print("Could not find the bot user to mention")
            await test_channel.send(f"@SWJ Options AI-Calculator {TEST_QUERY}")
        
        # Wait for the response (give it some time)
        await asyncio.sleep(10)
        
        print("Test complete. Please check the bot's response in the channel.")
        self.test_complete = True
        await self.close()
    
    async def on_message(self, message):
        """When a message is received, check if it's from the bot we're testing"""
        # Ignore messages from ourselves
        if message.author == self.user:
            return
        
        # Check if the message is from a bot named "SWJ Options AI-Calculator" or similar
        if message.author.bot and "SWJ" in message.author.name and "Options" in message.author.name:
            print(f"\nGot response from bot: {message.author.name}")
            
            # Check for embeds
            if message.embeds:
                for embed in message.embeds:
                    print(f"Embed Title: {embed.title}")
                    
                    # Check all fields to find the stop level info
                    for field in embed.fields:
                        if field.value and "Stock Price Stop Level" in field.value:
                            print(f"Found stop level field: {field.name}")
                            print(f"Content: {field.value}")
                            
                            # Check if the percentage is displayed correctly
                            if "below current price" in field.value or "above current price" in field.value:
                                print("✅ SUCCESS: Stop level percentage is displayed correctly!")
                            else:
                                print("❌ ERROR: Stop level percentage is not displayed correctly")
            else:
                print("No embeds found in the response.")
            
            # Set flag to exit after analyzing the response
            self.test_complete = True
            await self.close()

async def main():
    """Main function to run the test"""
    # Get the bot token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: No Discord token found in environment variables.")
        return
    
    # Create the test client
    intents = discord.Intents.default()
    intents.message_content = True
    client = TestClient(intents=intents)
    
    try:
        await client.start(token)
    except KeyboardInterrupt:
        await client.close()
    finally:
        if client.test_complete:
            print("Test completed.")
        else:
            print("Test ended unexpectedly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error running test: {e}")