"""
Test script to check live Discord bot responses

This script observes the bot's behavior in response to a test message
and verifies the field ordering.
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Global variables to track bot responses
last_bot_response = None
response_received = asyncio.Event()

class ResponseClient(discord.Client):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, *args, **kwargs)
        
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        print('Ready to test! Please enter the server ID and channel ID:')
        server_id = input('Server ID: ')
        channel_id = input('Channel ID: ')
        
        try:
            server_id = int(server_id)
            channel_id = int(channel_id)
            
            # Find the server and channel
            server = self.get_guild(server_id)
            if not server:
                print(f"Cannot find server with ID {server_id}")
                return
                
            channel = server.get_channel(channel_id)
            if not channel:
                print(f"Cannot find channel with ID {channel_id}")
                return
            
            # Send a test message to trigger the bot
            print(f"Sending test message to #{channel.name} in {server.name}")
            await channel.send("@SWJ Options AI-Calculator What's the stop loss for 3 TSLA $190 puts expiring next week?")
            
            # Wait for response for up to 30 seconds
            try:
                await asyncio.wait_for(response_received.wait(), timeout=30)
                if last_bot_response:
                    analyze_response(last_bot_response)
                else:
                    print("No response received but event was triggered (unexpected)")
            except asyncio.TimeoutError:
                print("Timed out waiting for bot response")
            
            await asyncio.sleep(2)  # Give a moment to see results
            await self.close()
            
        except ValueError:
            print("IDs must be numeric")
            await self.close()
        
    async def on_message(self, message):
        # Ignore messages from self
        if message.author.id == self.user.id:
            return
            
        # Check if this is our bot responding
        if message.author.name == "SWJ Options AI-Calculator":
            global last_bot_response
            global response_received
            
            print(f"Bot response received!")
            last_bot_response = message
            
            if hasattr(message, 'embeds') and message.embeds:
                response_received.set()
                
def analyze_response(message):
    """Analyze the bot's response to check field ordering"""
    if not hasattr(message, 'embeds') or not message.embeds:
        print("Response has no embeds")
        return
        
    embed = message.embeds[0]
    
    print(f"Embed title: {embed.title}")
    print(f"Embed description: {embed.description}")
    print(f"Number of fields: {len(embed.fields)}")
    
    print("\nFields in order:")
    for i, field in enumerate(embed.fields):
        print(f"Field #{i}: {field.name}")
    
    # Check if risk warning is the last field
    last_field = embed.fields[-1] if embed.fields else None
    if last_field and "RISK WARNING" in last_field.name:
        print("\n✅ Success: RISK WARNING is correctly positioned as the last field")
    else:
        print("\n❌ Error: RISK WARNING is NOT the last field")
        if last_field:
            print(f"Last field is: {last_field.name}")

async def main():
    client = ResponseClient()
    await client.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Test cancelled by user")