#!/usr/bin/env python3
"""
Test script to verify Discord bot output formatting for unusual options activity
"""
import asyncio
import re

# Reusing parts of the Discord bot testing code
class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = type('obj', (object,), {'id': 123456})
        self.channel = type('obj', (object,), {'id': 789012})
        self.replies = []
    
    async def reply(self, content):
        self.replies.append(content)
        print(f"\n=== DISCORD BOT REPLY ===\n{content}\n=====================\n")
        return None

async def test_unusual_activity(ticker="AAPL"):
    """
    Test Discord bot unusual options activity output formatting
    """
    print(f"\n===== Testing Discord Bot Unusual Activity Output for {ticker} =====\n")
    
    # Import the bot class here to avoid module-level imports
    from discord_bot import OptionsBot
    
    # Create a bot instance
    bot = OptionsBot()
    await bot.on_ready()  # Initialize the bot
    
    # Create a mock message with unusual activity request
    query = f"check unusual activity for {ticker}"
    message = MockMessage(query)
    
    # Process the message
    await bot.on_message(message)
    
    # Wait for processing to complete
    await asyncio.sleep(2)
    
    # Check if we got any replies
    if message.replies:
        reply = message.replies[0]
        
        # Check for required formatting elements
        format_checks = [
            ("✅" if "UNUSUAL BULLISH ACTIVITY" in reply or 
                    "UNUSUAL BEARISH ACTIVITY" in reply else "❌",
             "Uses proper emoji and title for activity type"),
            
            ("✅" if "strongly bullish activity for" in reply.lower() or 
                    "strongly bearish activity for" in reply.lower() else "❌",
             "Uses 'strongly bullish/bearish activity for [Ticker], Inc.' format"),
            
            ("✅" if "**million bullish**" in reply or 
                    "**million bearish**" in reply else "❌",
             "Bolds 'million bullish/bearish' text"),
            
            ("✅" if re.search(r"in-the-money \(\$\d+\.\d+\)", reply) else "❌",
             "Uses 'in-the-money ($245.00)' format"),
            
            ("✅" if re.search(r"occurred on \d{2}/\d{2}/\d{2}", reply) and
                    not re.search(r"occurred (on|at) \d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}", reply) else "❌",
             "Shows date without time component"),
            
            ("✅" if "Unusual activity score:" not in reply else "❌",
             "Does not show unusualness score")
        ]
        
        print("\n===== FORMAT VERIFICATION =====\n")
        for check_result, check_description in format_checks:
            print(f"{check_result} {check_description}")
    else:
        print("No reply received from the bot. Check for errors in the console.")

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    asyncio.run(test_unusual_activity(ticker))