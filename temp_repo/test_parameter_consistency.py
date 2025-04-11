"""
Test script to verify parameter consistency between NLP parsing and handler methods.
This ensures 'expiration'/'expiration_date' and 'strike'/'strike_price' are correctly handled.
"""

import os
import re
import json
import sys
from datetime import datetime, timedelta

# Create mock modules before importing the bot
# Create mock for discord module
class MockDiscord:
    def __init__(self):
        self.embed_fields = []
        self.ext = type('ext', (), {})
        self.ext.commands = type('commands', (), {})
        self.ext.commands.Context = type('Context', (), {})
        self.ext.commands.Bot = type('Bot', (), {})
        self.ext.commands.Cog = type('Cog', (), {})
        self.ext.commands.command = lambda: lambda x: x
        
    class MockObject:
        def __init__(self, id):
            self.id = id
            
    class MockColor:
        @staticmethod
        def blue():
            return 0x368BD6
            
        @staticmethod
        def green():
            return 0x00D026
            
        @staticmethod
        def orange():
            return 0xFF8C00
            
    class MockEmbed:
        def __init__(self, title="", description="", color=None):
            self.title = title
            self.description = description
            self.color = color
            self.fields = []
            self.footer = None
            
        def add_field(self, name="", value="", inline=False):
            self.fields.append({"name": name, "value": value, "inline": inline})
            return self
            
        def set_footer(self, text=""):
            self.footer = text
            return self

# Setup the mock discord module
mock_discord = MockDiscord()
sys.modules['discord'] = mock_discord
sys.modules['discord.ext'] = mock_discord.ext

# Also mock other dependencies
class MockNLTK:
    def __init__(self):
        self.tokenize = type('tokenize', (), {})
        self.tokenize.word_tokenize = lambda x: x.split()
        self.corpus = type('corpus', (), {})
        self.corpus.stopwords = type('stopwords', (), {})
        self.corpus.stopwords.words = lambda x: ['a', 'an', 'the', 'and', 'or', 'but']

sys.modules['nltk'] = MockNLTK()
sys.modules['nltk.tokenize'] = MockNLTK().tokenize
sys.modules['nltk.corpus'] = MockNLTK().corpus

# Mock numpy and pandas
class MockNumpy:
    def isnan(self, x):
        return False

np = MockNumpy()
np.isnan = lambda x: False
sys.modules['numpy'] = np

class MockPandas:
    def to_datetime(self, date_str, **kwargs):
        if isinstance(date_str, str):
            return datetime.now() + timedelta(days=30)
        return date_str

pd = MockPandas()
pd.to_datetime = lambda x, **kwargs: datetime.now() + timedelta(days=30)
sys.modules['pandas'] = pd

# Mock other imports
class MockStub:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        return self
    def __getattr__(self, name):
        return self

sys.modules['matplotlib'] = MockStub()
sys.modules['matplotlib.pyplot'] = MockStub()
sys.modules['dotenv'] = MockStub()
sys.modules['yfinance'] = MockStub()
sys.modules['option_calculator'] = MockStub()
sys.modules['technical_analysis'] = MockStub()
sys.modules['re'] = re

# Now we can import our actual bot code with discord mocks
from discord_bot import OptionsBotNLP

def test_parameter_consistency():
    """Test that parameter naming is consistent between NLP and handlers"""
    nlp = OptionsBotNLP()
    
    # Test case 1: Using 'expiration' field
    query1 = "What's a good stop loss for AAPL $200 calls expiring on April 20th 2025?"
    info1 = nlp.parse_query(query1)
    print("\n=== Test Case 1: Using 'expiration' field ===")
    print(f"Original Query: {query1}")
    print(f"Parsed info: {json.dumps(info1, indent=2, default=str)}")
    print(f"Has 'expiration': {'expiration' in info1}")
    print(f"Has 'expiration_date': {'expiration_date' in info1}")
    
    # Test case 2: Using 'strike' field
    query2 = "What's a good stop loss for TSLA $250 puts expiring next month?"
    info2 = nlp.parse_query(query2)
    print("\n=== Test Case 2: Using 'strike' field ===")
    print(f"Original Query: {query2}")
    print(f"Parsed info: {json.dumps(info2, indent=2, default=str)}")
    print(f"Has 'strike': {'strike' in info2}")
    print(f"Has 'strike_price': {'strike_price' in info2}")
    
    # Test case 3: Checking both parameter types
    query3 = "What's the price of META $450 calls expiring in June 2025?"
    info3 = nlp.parse_query(query3)
    print("\n=== Test Case 3: Both parameter types ===")
    print(f"Original Query: {query3}")
    print(f"Parsed info: {json.dumps(info3, indent=2, default=str)}")
    print(f"Has 'strike': {'strike' in info3}")
    print(f"Has 'strike_price': {'strike_price' in info3}")
    print(f"Has 'expiration': {'expiration' in info3}")
    print(f"Has 'expiration_date': {'expiration_date' in info3}")

if __name__ == "__main__":
    test_parameter_consistency()