"""
Test script to verify that duplicate risk warnings have been fixed
"""

import os
import sys
import discord
import traceback
from datetime import datetime, timedelta
import re

# To avoid actually submitting Discord messages
test_mode = True  # Set to False to actually send messages to Discord (not recommended)

async def run_test():
    """Run a test query to check if duplicate risk warnings have been fixed"""
    try:
        # Import our bot
        from discord_bot import OptionsBotNLP, OptionsBot
        
        # Initialize our bot components
        nlp = OptionsBotNLP()
        bot = OptionsBot()
        
        # Mock message classes
        class MockUser:
            def __init__(self):
                self.mention = "@user"
                self.id = 12345
                self.bot = False
        
        class MockChannel:
            def __init__(self):
                self.id = 67890
                self.name = "test-channel"
                
            async def send(self, content=None, embed=None):
                print("Channel.send called")
                if embed:
                    analyze_embed(embed)
                return None
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
                self.author = MockUser()
                self.channel = MockChannel()
            
            async def reply(self, content=None, embed=None):
                print("Message.reply called")
                if embed:
                    analyze_embed(embed)
                return None
        
        def analyze_embed(embed):
            """Check for duplicate risk warnings in the embed"""
            print(f"\nAnalyzing embed: {embed.title}")
            
            if not hasattr(embed, 'fields') or len(embed.fields) == 0:
                print("Embed has no fields")
                return
                
            fields = []
            risk_warning_count = 0
            risk_warning_positions = []
            
            for i, field in enumerate(embed.fields):
                fields.append(field.name)
                print(f"Field #{i+1}: {field.name}")
                if "RISK WARNING" in field.name:
                    risk_warning_count += 1
                    risk_warning_positions.append(i+1)
            
            print(f"\nFound {risk_warning_count} risk warning fields at positions: {risk_warning_positions}")
            
            if risk_warning_count > 1:
                print("❌ ERROR: Found multiple risk warning fields!")
            elif risk_warning_count == 0:
                print("❌ ERROR: No risk warning field found!")
            else:
                print("✅ SUCCESS: Exactly one risk warning field found")
                
                # Check if it's the last field
                if risk_warning_positions[0] == len(fields):
                    print("✅ SUCCESS: Risk warning is correctly positioned as the last field")
                else:
                    print(f"❌ ERROR: Risk warning is not the last field! Found at position {risk_warning_positions[0]} of {len(fields)}")
        
        # Test with AMD calls with a January 2026 expiration (trigger long-term format)
        test_query = "What's the stop loss for AMD $200 calls expiring Jan 16th, 2026?"
        print(f"Testing query: '{test_query}'")
        
        # Parse the query using the NLP component
        request_type, info = nlp.parse_query(test_query)
        print(f"Query parsed as: {request_type}")
        print(f"Extracted info: {info}")
        
        # Create a mock message for the bot
        message = MockMessage(test_query)
        
        # Test handling stop loss request directly
        print("\nTesting handle_stop_loss_request...")
        if request_type == 'stop_loss' and info and info.get('ticker'):
            await bot.handle_stop_loss_request(message, info)
        else:
            print("ERROR: Query did not parse as a stop loss request for a valid ticker")
    
    except Exception as e:
        print(f"ERROR in test: {str(e)}")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    # Run the test using asyncio
    import asyncio
    asyncio.run(run_test())