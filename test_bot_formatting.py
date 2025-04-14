"""
Test Discord bot's unusual options activity output formatting
This simulates sending a message to the bot and captures the output format
"""

import discord
import asyncio
import re
import discord_bot
from discord_bot import OptionsBot

class MockUser:
    """Mock Discord user"""
    def __init__(self):
        self.id = 12345
        self.name = "TestUser"
        self.mentioned_in_reply = False
        
    async def send(self, content=None, embed=None):
        self.last_dm = content
        return MockMessage(content)

class MockChannel:
    """Mock Discord channel"""
    def __init__(self):
        self.id = 67890
        self.sent_messages = []
        
    async def send(self, content=None, embed=None):
        self.sent_messages.append(content if content else embed.description if embed else "")
        msg = MockMessage("", user=None, channel=self)
        msg.content = content
        msg.embed = embed
        return msg

class MockMessage:
    """Mock Discord message"""
    def __init__(self, content, user=None, channel=None):
        self.content = content
        self.author = user or MockUser()
        self.channel = channel or MockChannel()
        self.replied = False
        self.reply_content = None
        self.reply_embed = None
        
    async def reply(self, content=None, embed=None, mention_author=True):
        self.replied = True
        self.reply_content = content
        self.reply_embed = embed
        self.author.mentioned_in_reply = mention_author
        
        if content:
            print("\n===== BOT RESPONSE =====")
            print(content)
            print("========================\n")
            
            # Check formatting requirements
            check_formatting(content)
        
        if embed:
            print(f"Title: {embed.title}")
            print(f"Description: {embed.description}")
            for field in embed.fields:
                print(f"{field.name}: {field.value}")
                
        return MockMessage(content, self.author, self.channel)

def check_formatting(content):
    """Check if the content meets the required formatting standards"""
    checks = {
        "Strike price format": (
            r'in-the-money \((\d+\.\d+)\)',
            lambda m: f"✅ Found numeric strike price: {m.group(0)}" if m else "❌ Missing numeric strike price"
        ),
        "Expiration date format": (
            r'expiring (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found MM/DD/YY expiration: {m.group(0)}" if m else "❌ Missing MM/DD/YY expiration"
        ),
        "Purchase date": (
            r'purchased (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found purchase date: {m.group(0)}" if m else "❌ Missing purchase date"
        ),
        "No bet wording": (
            r'bullish bet|bearish bet',
            lambda m: "❌ Contains unwanted 'bet' wording" if m else "✅ No 'bet' wording"
        ),
        "No 'occurred at'": (
            r'occurred at',
            lambda m: "❌ Contains unwanted 'occurred at' text" if m else "✅ No 'occurred at' text"
        ),
        "No 'on' before date": (
            r'expiring on',
            lambda m: "❌ Contains unwanted 'expiring on' text" if m else "✅ No 'expiring on' text"
        ),
        "No ticker in strike": (
            r'in-the-money \(\$[A-Z]+',
            lambda m: "❌ Contains ticker symbol in strike price" if m else "✅ No ticker in strike price"
        ),
        "No X-the-money format": (
            r'\d+-the-money',
            lambda m: "❌ Contains X-the-money format" if m else "✅ No X-the-money format"
        ),
        "Has bolded millions": (
            r'\*\*\$\d+\.\d+ million (bullish|bearish)\*\*',
            lambda m: f"✅ Properly bolded millions: {m.group(0)}" if m else "❌ Missing bolded millions"
        )
    }
    
    # Run all checks
    all_passed = True
    print("\n===== FORMAT CHECKS =====")
    for check_name, (pattern, result_fn) in checks.items():
        match = re.search(pattern, content)
        
        # For 'No X' checks, we want match to be None
        expected_match = "No" not in check_name
        
        if (match and expected_match) or (not match and not expected_match):
            print(f"{check_name}: {result_fn(match)}")
        else:
            all_passed = False
            if "No" in check_name and match:
                # For 'No X' checks, finding a match is a failure
                print(f"{check_name}: ❌ Found forbidden pattern: {match.group(0)}")
            else:
                print(f"{check_name}: {result_fn(match)}")
    
    # Overall result
    if all_passed:
        print("\n✅ ALL FORMAT REQUIREMENTS PASSED!")
    else:
        print("\n❌ SOME FORMAT REQUIREMENTS FAILED!")
    print("=======================\n")

async def test_unusual_options():
    """Test the unusual options formatting in the Discord bot"""
    print("Testing Discord bot unusual options formatting for TSLA...")
    
    # Initialize bot with mock methods
    bot = OptionsBot()
    
    # Mock auth methods
    bot.is_channel_whitelisted = lambda channel_id: True
    bot.is_admin = lambda user_id: True
    
    # Create NLP processor 
    nlp = discord_bot.OptionsBotNLP()
    
    # Create test query and message
    query = "show me unusual options for TSLA"
    user = MockUser()
    channel = MockChannel()
    message = MockMessage(query, user, channel)
    
    # Parse the query
    parsed = nlp.parse_query(query)
    
    # Call the handler directly
    print("Calling unusual activity handler...")
    await bot.handle_unusual_activity_request(message, parsed)
    
    # Check results
    if message.replied:
        print("Bot successfully responded to the request")
    else:
        print("❌ Bot did not reply to the message")

def run_test():
    """Run the async test"""
    # Monkey patch Discord bot to avoid connection issues
    discord_bot.OptionsBot.__init__ = lambda self: None
    
    try:
        # Run the test
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_unusual_options())
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    run_test()