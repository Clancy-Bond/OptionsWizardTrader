"""
Fixed version of discord_bot.py with properly implemented handle_stop_loss_request method.
"""

# Import discord modules
import discord
from discord.ext import commands

# Import numerical and data processing libraries
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
# Import LookupError from standard library
# NLTK will raise this when a resource is missing
import os
import re
import json
import random
from datetime import datetime, date, timedelta
import time
import sys
from collections import defaultdict

# Load environment variables
load_dotenv()

# Define constants
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Try to download NLTK data, but proceed even if it fails
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    print(f"NLTK download error: {str(e)}")

class OptionsBotNLP:
    """Natural Language Processor for understanding options-related queries"""
    
    def __init__(self):
        print("Initializing OptionsBotNLP")
        # Load stopwords
        try:
            self.stop_words = set(stopwords.words('english'))
            print(f"Loaded {len(self.stop_words)} stop words")
        except Exception as e:
            print(f"Error loading stopwords: {str(e)}")
            # Fallback to a minimal set
            self.stop_words = set(['a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by', 'for', 'with', 'about'])
            print(f"Fallback: loaded {len(self.stop_words)} stop words")
        
        # Define keywords that indicate different request types with expanded vocabulary
        self.option_price_keywords = {
            'option', 'price', 'value', 'worth', 'cost', 'pricing', 'calculate', 'estimate', 
            'premium', 'fair', 'call', 'put', 'pay', 'expir', 'strike', 'profit', 'loss', 'gain',
            'return', 'make', 'breakeven', 'break-even', 'break', 'even', 'what', 'how', 'much',
            'would', 'will', 'future', 'projection', 'estimate', 'calculation', 'analyze', 'calc',
            'valuation', 'potential', 'growth', 'decay', 'performance', 'opportunity', 'investment',
            'market', 'shares', 'contract', 'contracts', 'trading', 'trade', 'strategy', 'buying',
            'selling', 'invest', 'entry', 'setup', 'priced', 'valued', 'current', 'today', 'now',
            'money', 'in-the-money', 'itm', 'otm', 'out-the-money', 'spread', 'underlying'
        }
        
        self.stop_loss_keywords = {
            'stop', 'loss', 'recommendation', 'recommend', 'reccomendation', 'reccomend', 
            'exit', 'cut', 'limit', 'downside', 'protect', 'protection', 'hedge', 'risk', 'manage', 
            'profit', 'secure', 'lock', 'target', 'safety', 'safe', 'prevent', 'avoid', 'minimize',
            'mitigate', 'threshold', 'point', 'level', 'maximum', 'bail', 'out', 'ceiling', 'floor',
            'worst', 'case', 'scenario', 'danger', 'when', 'sell', 'selling', 'sold', 'dump',
            'defensive', 'guard', 'shield', 'insurance', 'insure', 'safeguard', 'escape', 'pullback',
            'retreat', 'withdraw', 'acceptable', 'tolerable', 'threshold', 'control', 'protect',
            'preserve', 'capital', 'investment', 'drop', 'decline', 'fall', 'crash', 'drawdown',
            'position', 'close', 'unwind', 'liquidate', 'exit-strategy', 'get-out', 'margin',
            'danger-zone', 'red-line', 'bottom', 'damage', 'defense', 'recover', 'reversal'
        }
        
        self.unusual_activity_keywords = {
            'unusual', 'activity', 'whale', 'flow', 'sweep', 'block', 'large', 'institutional',
            'smart', 'money', 'option', 'volume', 'interest', 'sentiment', 'activity', 'big',
            'player', 'institution', 'hedge', 'fund', 'unusual', 'abnormal', 'spike', 'surge',
            'heavy', 'trading', 'insider', 'market', 'maker', 'signal', 'indicator', 'significant',
            'alert', 'anomaly', 'noteworthy', 'important', 'rare', 'strange', 'extreme', 'outlier',
            'outstanding', 'remarkable', 'notable', 'exceptional', 'major', 'mega', 'critical',
            'momentum', 'pattern', 'trend', 'breakout', 'breakthrough', 'movement', 'shift',
            'attention', 'monitor', 'watch', 'spot', 'detect', 'identify', 'tracking', 'flagged',
            'highlight', 'flagging', 'screening', 'scanner', 'radar', 'unusual-options', 'dark-pool'
        }
        
        print(f"- option_price keywords: {', '.join(sorted(list(self.option_price_keywords))[:3])}...")
        print(f"- stop_loss keywords: {', '.join(sorted(list(self.stop_loss_keywords))[:3])}...")
        print(f"- unusual_activity keywords: {', '.join(sorted(list(self.unusual_activity_keywords))[:3])}...")
        
        # Regular expressions for extracting information - enhanced for more natural language patterns
        
        # Extract ticker symbols (1-5 uppercase letters, not followed by common word endings)
        # Also matches ticker explicitly mentioned with $ prefix or in phrases like "for AAPL"
        self.ticker_pattern = r'(?:(?:ticker|symbol|stock|for|on|in|of|the)\s+)?(?:\$)?([A-Z]{1,5})(?!\w+\b)\b'
        
        # Extract option type (call or put) - case insensitive with more variations
        self.option_type_pattern = r'\b(calls?|puts?|c(?:all)?|p(?:ut)?)\b'
        
        # Extract option premium - amount paid for the option with more variations
        self.premium_pattern = r'(?:paid|premium|bought|cost|price|for|at)[^\d]+([\d.,]+)(?:\s?(?:dollars|USD|\$)?)'
        
        # Extract strike price with optional $ sign, ensure we don't match Discord IDs
        # Also handle phrases like "strike price of X" or "with a strike of X"
        self.strike_pattern = r'(?:(?:strike|at|for)(?:\s+price)?(?:\s+of)?)?(?:\s+at)?\s+(?<!\d)(?:\$)?(\d+(?:\.\d+)?)(?!\d)'
        
        # Enhanced expiration date pattern to handle more natural language variations
        # This handles formats like:
        # - January 15
        # - Jan 15th
        # - 01/15
        # - 15th of January
        # - expiring next Friday
        # - this Friday
        # - January 15, 2025
        # - 2025-01-15
        # - Jan 15 2025
        # - 15 Jan 2025
        # - expiration of May 2nd 
        # - expires on May 2
        # - expiration of 2025-05-02
        self.expiration_pattern = r'(?:expir(?:ing|es?|ation)|exp|dated?|on|for|at|to|until|by|maturity|due|ends?)[: ]?(?:\s+(?:of|on|in|at|for|by|until))?\s+((?:(?:this|next|coming)\s+(?:mon|tues|wednes|thurs|fri|satur|sun)(?:day)?|tomorrow|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?(?:[,]?\s+\d{2,4})?|\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:[,]?\s+\d{2,4})?|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\d{4}[/-]\d{1,2}[/-]\d{1,2}))'
        
        # Extract target price with more variations including phrases
        self.target_pattern = r'(?:to|target|price target|go(?:ing)? to|reach(?:es)?|hit(?:s)?|if it (?:goes|hits|reaches)|when it (?:goes|hits|reaches))(?:\s+a price)?[^\d]+([\d.,]+)(?:\s?(?:dollars|USD|\$)?)'
        
        # Extract number of contracts with more variations
        self.contracts_pattern = r'(\d+)(?:\s+)?(?:contracts?|positions?|options?|lots?|shares?)'
        
        # Extract trade horizon with more variations and phrases
        self.trade_horizon_pattern = r'\b(scal(?:p(?:ing)?)?|intra(?:day)?|day[ -]?trad(?:ing|e)?|swing[ -]?trad(?:ing|e)?|short[ -]term|medium[ -]term|long[ -]term|leap(?:s)?|position|invest(?:ment)?|(?:1|one|two|three|four|five)\s+(?:day|week|month|year))\b'
        
    def preprocess_text(self, text):
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Directly use our own tokenization, no longer trying to use NLTK's tokenizer
        # which has issues with punkt_tab
        import re
        tokens = re.findall(r'\b\w+\b', text)
        
        # Remove stopwords and punctuation
        filtered_tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
        return filtered_tokens
    
    def identify_request_type(self, tokens):
        """Identify the type of request from the tokens"""
        # Get raw text of all tokens joined
        raw_text = ' '.join(tokens).lower()
        original_text = raw_text  # Keep original for regex checks
        
        # HIGHEST PRIORITY: Check for explicit stop loss keywords and phrases
        stop_loss_phrases = [
            'stop loss', 'stop-loss', 'stoploss', 'recommendation', 'reccomendation', 
            'when to exit', 'when to sell', 'exit point', 'exit strategy', 'cut losses',
            'minimize risk', 'risk management', 'protect profit', 'bailout', 'bail out',
            'downside protection', 'maximum loss', 'manage risk', 'where to exit'
        ]
        
        if any(phrase in raw_text for phrase in stop_loss_phrases):
            print(f"NLP: Detected stop loss request based on high priority phrase match")
            return 'stop_loss'
        
        # Use regex to find stop loss patterns in natural language
        stop_loss_patterns = [
            r'where.+should.+(exit|sell|cut|stop)', 
            r'when.+should.+(exit|sell|cut|stop)', 
            r'what.+(exit|sell).+strategy',
            r'how.+much.+(risk|loss)',
            r'protect.+(investment|profit|gains)',
            r'(exit|sell).+if.+(drops|falls|declines)',
            r'risk.+management.+strategy',
            r'avoid.+(big|large|significant).+loss',
            r'stop.+out.+point'
        ]
        
        for pattern in stop_loss_patterns:
            if re.search(pattern, raw_text):
                print(f"NLP: Detected stop loss request based on regex pattern: {pattern}")
                return 'stop_loss'
        
        # HIGH PRIORITY: Check for questions about risk
        risk_phrases = ['risk', 'risky', 'downside', 'danger', 'safe', 'safety', 'lose']
        question_words = ['what', 'how', 'where', 'when', 'is', 'should']
        
        has_risk_word = any(word in raw_text for word in risk_phrases)
        has_question_word = any(word in raw_text.split()[:3] for word in question_words)  # Check if question word is in first 3 words
        
        if has_risk_word and has_question_word:
            print(f"NLP: Detected stop loss request based on risk question pattern")
            return 'stop_loss'
           
        # Count keyword matches for each request type with weighting
        # Stop loss keywords get higher weight for priority
        option_price_count = sum(1 for token in tokens if token in self.option_price_keywords)
        stop_loss_count = sum(1.5 for token in tokens if token in self.stop_loss_keywords)  # 50% higher weight
        unusual_activity_count = sum(1 for token in tokens if token in self.unusual_activity_keywords)
        
        print(f"NLP: Weighted keyword count - option_price: {option_price_count}, stop_loss: {stop_loss_count}, unusual: {unusual_activity_count}")
        
        # Determine the request type based on the highest count, but prioritize stop_loss if it has any score
        if stop_loss_count > 0:
            print("NLP: Prioritizing stop loss request based on weighted keywords (count > 0)")
            return 'stop_loss'
        elif option_price_count > unusual_activity_count:
            # Double check if there are any stop loss indicators in the text
            if any(word in raw_text for word in ['stop', 'loss', 'exit', 'risk', 'sell', 'protect']):
                print("NLP: Overriding to stop loss due to presence of key stop loss words")
                return 'stop_loss'
            print("NLP: Detected option price request based on keyword counts")
            return 'option_price'
        elif unusual_activity_count > option_price_count:
            print("NLP: Detected unusual activity request based on keyword counts")
            return 'unusual_activity'
        else:
            # If counts are equal or no significant matches, look for specific patterns
            
            # Check for sell/exit verbs combined with condition words
            sell_verbs = ['sell', 'exit', 'dump', 'drop', 'get out', 'bail']
            condition_words = ['if', 'when', 'before', 'after', 'should', 'below', 'above', 'at']
            
            if any(verb in raw_text for verb in sell_verbs) and any(cond in raw_text for cond in condition_words):
                print("NLP: Detected stop loss request based on sell verb + condition pattern")
                return 'stop_loss'
            
            # Enhanced stop loss detection - check for individual keywords with higher precedence
            if ('stop' in raw_text) or ('loss' in raw_text) or ('exit' in raw_text) or ('sell' in raw_text and 'when' in raw_text):
                print("NLP: Detected stop loss request based on individual keywords")
                return 'stop_loss'
            # Check for explicit price inquiries
            elif ('price' in raw_text or 'worth' in raw_text or 'cost' in raw_text) and not ('stop' in raw_text or 'loss' in raw_text):
                print("NLP: Detected option price request based on keywords")
                return 'option_price'
            # Check for unusual activity
            elif ('unusual' in raw_text or 'whale' in raw_text) and 'activity' in raw_text:
                print("NLP: Detected unusual activity request based on keywords")
                return 'unusual_activity'
            # Final fallback for option type
            elif 'option' in raw_text:
                # Check if any stop loss related words are in the context
                if any(kw in raw_text for kw in ['stop', 'loss', 'exit', 'recommendation', 'reccomendation', 'risk', 'protect']):
                    print("NLP: Detected stop loss request based on context with 'option'")
                    return 'stop_loss'
                else:
                    print("NLP: Fallback to option price for message with 'option'")
                    return 'option_price'
            else:
                print("NLP: Could not determine request type")
                return 'unknown'
    
    def extract_info(self, text):
        """Extract relevant information from text using patterns"""
        info = {}
        
        # Extract ticker symbol - find all matches and filter common words
        ticker_matches = re.findall(self.ticker_pattern, text)
        common_words = {'FOR', 'THE', 'AND', 'ITS', 'THIS', 'LIKE', 'WITH', 'FROM', 'HAVE', 'THAT'}
        
        filtered_tickers = [ticker for ticker in ticker_matches if ticker not in common_words]
        if filtered_tickers:
            info['ticker'] = filtered_tickers[0]
        
        # Extract option type
        option_type_match = re.search(self.option_type_pattern, text.lower())
        if option_type_match:
            option_type = option_type_match.group(1).lower()
            # Normalize to just "call" or "put"
            info['option_type'] = 'call' if option_type.startswith('call') else 'put'
        
        # Extract premium
        premium_match = re.search(self.premium_pattern, text.lower())
        if premium_match:
            try:
                info['premium'] = float(premium_match.group(1))
            except ValueError:
                pass
        
        # Extract strike price
        # We need to be careful with strike price extraction to avoid false positives
        strike_matches = re.findall(self.strike_pattern, text)
        if strike_matches:
            # Filter strikes by context - look for "strike", "$", or "call/put" nearby
            strike_candidates = []
            for i, strike in enumerate(strike_matches):
                try:
                    strike_val = float(strike)
                    strike_pos = text.find(strike)
                    context = text[max(0, strike_pos-20):min(len(text), strike_pos+20)]
                    
                    if ('strike' in context.lower() or '$' in context or 
                        'call' in context.lower() or 'put' in context.lower()):
                        strike_candidates.append(strike_val)
                except ValueError:
                    continue
            
            if strike_candidates:
                info['strike'] = strike_candidates[0]
            elif strike_matches:
                # Fallback to first match if no good context
                try:
                    info['strike'] = float(strike_matches[0])
                except ValueError:
                    pass
        
        # Extract expiration date
        expiration_match = re.search(self.expiration_pattern, text.lower())
        if expiration_match:
            # Store raw expiration text for now, we'll parse it later
            info['expiration_raw'] = expiration_match.group(1)
        
        # Extract target price
        target_match = re.search(self.target_pattern, text.lower())
        if target_match:
            try:
                info['target_price'] = float(target_match.group(1))
            except ValueError:
                pass
        
        # Extract number of contracts
        contracts_match = re.search(self.contracts_pattern, text.lower())
        if contracts_match:
            try:
                info['contracts'] = int(contracts_match.group(1))
            except ValueError:
                pass
        else:
            # Default to 1 contract
            info['contracts'] = 1
        
        # Extract trade horizon
        horizon_match = re.search(self.trade_horizon_pattern, text.lower())
        if horizon_match:
            horizon = horizon_match.group(1).lower()
            # Normalize trade horizon
            if 'scalp' in horizon or 'day' in horizon:
                info['trade_horizon'] = 'scalp'
            elif 'swing' in horizon:
                info['trade_horizon'] = 'swing'
            elif 'long' in horizon or 'leap' in horizon:
                info['trade_horizon'] = 'longterm'
            else:
                info['trade_horizon'] = 'unknown'
        
        return info
    
    def parse_relative_dates(self, text, info):
        """Parse relative date references like 'next Friday', 'tomorrow', etc."""
        if 'expiration_raw' not in info:
            return info
        
        raw_date = info['expiration_raw'].lower()
        today = datetime.now()
        
        # Remove ordinal suffixes (1st, 2nd, 3rd, 4th, etc.) before parsing
        raw_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', raw_date)
        
        # Try to parse explicit month and day formats first
        try:
            # For formats like "Jan 21" or "January 21, 2023"
            date_parts = raw_date.split()
            if len(date_parts) >= 2:
                month_str = date_parts[0][:3]  # Take first 3 chars of month
                day_str = ''.join(filter(str.isdigit, date_parts[1]))  # Extract digits from day part
                
                # Map month abbreviation to month number
                month_map = {
                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                }
                
                if month_str in month_map and day_str:
                    month = month_map[month_str]
                    day = int(day_str)
                    
                    # Determine year - if date is in the past, assume next year
                    year = today.year
                    if month < today.month or (month == today.month and day < today.day):
                        year += 1
                        
                    # If year is explicitly mentioned, use that
                    if len(date_parts) >= 3 and date_parts[2].isdigit():
                        explicit_year = int(date_parts[2])
                        if explicit_year < 100:  # Handle 2-digit years
                            explicit_year += 2000
                        year = explicit_year
                        
                    expiration_date = datetime(year, month, day)
                    info['expiration'] = expiration_date.strftime('%Y-%m-%d')
                    return info
        except Exception as e:
            print(f"Error parsing explicit date: {str(e)}")
        
        # Special case for YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', raw_date):
            try:
                # This is YYYY-MM-DD format
                date_parts = raw_date.split('-')
                year = int(date_parts[0])
                month = int(date_parts[1])
                day = int(date_parts[2])
                expiration_date = datetime(year, month, day)
                info['expiration'] = expiration_date.strftime('%Y-%m-%d')
                return info
            except Exception as e:
                print(f"Error parsing ISO date format: {str(e)}")
                
        # Try to parse numerical formats like MM/DD or MM/DD/YY
        try:
            if '/' in raw_date or '-' in raw_date:
                # Replace both slashes and hyphens with slashes for consistent parsing
                normalized_date = raw_date.replace('-', '/')
                date_parts = normalized_date.split('/')
                
                if len(date_parts) >= 2:
                    # For MM/DD format
                    if len(date_parts[0]) <= 2 and len(date_parts[1]) <= 2:
                        month = int(date_parts[0])
                        day = int(date_parts[1])
                        
                        # Determine year
                        year = today.year
                        if len(date_parts) >= 3:
                            year_str = date_parts[2]
                            if len(year_str) <= 2:
                                year = 2000 + int(year_str)
                            else:
                                year = int(year_str)
                        elif month < today.month or (month == today.month and day < today.day):
                            year += 1
                            
                        expiration_date = datetime(year, month, day)
                        info['expiration'] = expiration_date.strftime('%Y-%m-%d')
                        return info
        except Exception as e:
            print(f"Error parsing numeric date: {str(e)}")
            
        # Handle relative dates
        try:
            if 'tomorrow' in raw_date:
                expiration_date = today + timedelta(days=1)
                info['expiration'] = expiration_date.strftime('%Y-%m-%d')
            elif 'next week' in raw_date:
                expiration_date = today + timedelta(days=7)
                info['expiration'] = expiration_date.strftime('%Y-%m-%d')
            elif 'next friday' in raw_date:
                # Calculate days until next Friday
                days_until_friday = (4 - today.weekday()) % 7
                if days_until_friday == 0:  # If today is Friday, get next Friday
                    days_until_friday = 7
                expiration_date = today + timedelta(days=days_until_friday)
                info['expiration'] = expiration_date.strftime('%Y-%m-%d')
            elif 'this friday' in raw_date:
                # Calculate days until this Friday
                days_until_friday = (4 - today.weekday()) % 7
                expiration_date = today + timedelta(days=days_until_friday)
                info['expiration'] = expiration_date.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error parsing relative date: {str(e)}")
            
        # If we couldn't parse the date, remove the raw field
        if 'expiration' not in info:
            info.pop('expiration_raw', None)
            
        return info
    
    def parse_query(self, query):
        """Parse the user query to identify the request type and extract information"""
        # Output query for debugging
        print(f"NLP: Parsing query: '{query}'")
        
        # Special case for stop loss recommendation
        query_lower = query.lower()
        
        # Expanded direct pattern matching for stop loss detection
        stop_loss_direct_patterns = [
            r'stop\s+loss',
            r'stop-loss',
            r'stoploss', 
            r'recommendation',
            r'reccomendation',
            r'exit\s+strategy',
            r'exit\s+plan',
            r'risk\s+management',
            r'exit\s+when',
            r'sell\s+when',
            r'when\s+to\s+exit',
            r'when\s+to\s+sell',
            r'protect\s+my\s+investment',
            r'manage\s+risk',
            r'minimize\s+loss',
            r'avoid\s+loss'
        ]
        
        # Check for direct stop loss patterns before tokenization
        direct_stop_loss_detected = False
        for pattern in stop_loss_direct_patterns:
            if re.search(pattern, query_lower):
                print(f"NLP: Direct detection of stop loss from pattern: {pattern}")
                direct_stop_loss_detected = True
                break
        
        # Preprocess text
        tokens = self.preprocess_text(query)
        
        # Identify request type using our enhanced algorithm
        request_type = self.identify_request_type(tokens)
        print(f"NLP: Initial request type identification: {request_type}")
        
        # Extract information with enhanced regex patterns
        info = self.extract_info(query)
        
        # Parse relative dates if present with improved date handling
        info = self.parse_relative_dates(query, info)
        
        # Direct override for clear stop loss requests regardless of other factors
        if direct_stop_loss_detected or "stop loss" in query_lower or "recommendation" in query_lower or "reccomendation" in query_lower:
            print("NLP: Override - setting request_type to stop_loss")
            request_type = 'stop_loss'
        
        # Check for question patterns about selling points or exit strategies
        exit_question_patterns = [
            r'when\s+(?:should|would|do|could|can|will)\s+(?:i|we|you|one|someone)\s+(?:sell|exit|dump|get rid of)',
            r'(?:tell|show|give)\s+(?:me|us)\s+(?:a|the)\s+(?:good|best|optimal|recommended)\s+(?:time|point|price|level)\s+to\s+(?:sell|exit)', 
            r'(?:what|where)\s+(?:is|would be|should be)\s+(?:a|the|my)\s+(?:good|best|optimal|recommended)\s+(?:exit|sell)',
            r'how\s+(?:do|can|should|would)\s+(?:i|we|you|one)\s+(?:determine|know|tell|decide)\s+when\s+to\s+(?:sell|exit)',
            r'(?:if|when)\s+(?:the|my|this)\s+(?:stock|etf|option|position)\s+(?:goes|falls|drops|declines|decreases)\s+(?:below|under|to|past)'
        ]
        
        for pattern in exit_question_patterns:
            if re.search(pattern, query_lower):
                print(f"NLP: Override - setting request_type to stop_loss due to exit question pattern")
                request_type = 'stop_loss'
                break
        
        # Add request type to the info
        info['request_type'] = request_type
        
        # Ensure parameter naming consistency - handle 'strike' vs 'strike_price'
        if 'strike' in info and info['strike'] is not None:
            info['strike_price'] = info['strike']
        
        # Ensure parameter naming consistency - handle 'expiration' vs 'expiration_date'
        if 'expiration' in info and info['expiration'] is not None:
            info['expiration_date'] = info['expiration']
        
        # Log findings for debugging
        print(f"NLP: Extracted info: {info}")
        print(f"NLP: Final request_type determined as: {request_type}")
        
        return info

class OptionsBot:
    def enforce_buffer_limits(self, stop_loss, current_price, option_type, days_to_expiration):
        # Calculate the current buffer percentage from the given stop_loss
        if option_type.lower() == 'call':
            # For calls, buffer is how far below current price
            current_buffer_percentage = (current_price - stop_loss) / current_price * 100
        else:
            # For puts, buffer is how far above current price
            current_buffer_percentage = (stop_loss - current_price) / current_price * 100
            
        # Determine the maximum allowed buffer based on DTE
        if days_to_expiration <= 1:
            max_buffer_percentage = 1.0  # 1% for 0-1 DTE
        elif days_to_expiration <= 2:
            max_buffer_percentage = 2.0  # 2% for 2 DTE
        elif days_to_expiration <= 5:
            max_buffer_percentage = 3.0  # 3% for 3-5 DTE
        elif days_to_expiration <= 60:
            max_buffer_percentage = 5.0  # 5% for medium-term
        else:
            max_buffer_percentage = 7.0 if option_type.lower() == 'put' else 5.0  # 7% for long-term puts, 5% for calls
            
        # Check if current buffer exceeds the maximum allowed
        if current_buffer_percentage > max_buffer_percentage:
            # Apply the maximum allowed buffer instead
            if option_type.lower() == 'call':
                # For calls, stop loss is below current price
                adjusted_stop_loss = current_price * (1 - max_buffer_percentage/100)
            else:
                # For puts, stop loss is above current price
                adjusted_stop_loss = current_price * (1 + max_buffer_percentage/100)
                
            # Calculate how much we're adjusting the stop loss by
            adjustment_percentage = abs(adjusted_stop_loss - stop_loss) / current_price * 100
            # Calculate how much we're adjusting (absolute percentage of current price)
            adjustment_percentage = abs(adjusted_stop_loss - stop_loss) / current_price * 100
            
            # Only log if adjustment is significant (greater than 0.01%)
            if adjustment_percentage > 0.01:
                print(f"Adjusting stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE")
                print(f"Current price: ${current_price:.2f}, adjustment amount: {adjustment_percentage:.2f}% of price")
            print(f"Current price: ${current_price:.2f}, adjustment amount: {adjustment_percentage:.2f}% of price")
            return adjusted_stop_loss
            
        # If current buffer is within limits, return original stop loss
        return stop_loss
    
    """Main Options Bot class to handle user requests"""
    
    def __init__(self):
        # Initialize NLP processor
        self.nlp = OptionsBotNLP()
        
        # STRICT CHANNEL RESTRICTION
        # The bot will ONLY respond in the "ai-options-calculator" channel
        # This is a STRICT restriction - do not change without explicit permission
        self.approved_channels = ["ai-options-calculator"]  # ONLY "ai-options-calculator" channel is allowed
        
    def get_help_instructions(self):
        """Return help instructions for interacting with the bot"""
        help_text = """**SWJ Options AI-Calculator Help**

I'm an Options Analysis bot that can help you with options trading information. Here's what I can do:

**1️⃣ Option Price Estimation**
Example: "@SWJ Options AI-Calculator What's the price of AAPL $180 calls expiring next Friday?"

**2️⃣ Stop Loss Recommendations**
Example: "@SWJ Options AI-Calculator What's a good stop loss for my TSLA $240 calls expiring Aug 18?"

**3️⃣ Unusual Options Activity**
Example: "@SWJ Options AI-Calculator Show me unusual options activity for MSFT"

**Required Parameters:**
For stop loss recommendations, you MUST include all these details:
• Ticker symbol (e.g., AAPL, TSLA)
• Option type (calls or puts)
• Strike price (e.g., $240)
• Expiration date (e.g., Aug 18, 2025-06-20)

To use me, just mention me (@SWJ Options AI-Calculator) and ask your question in natural language.

IMPORTANT: I only respond when directly mentioned in the #blank1 channel or its threads."""
        
        return help_text
        
    async def handle_message(self, message):
        """Process user message and generate a response using consistent Discord embeds"""
        import discord
        import re
        
        # STRICT CHANNEL RESTRICTION - Only respond in Blank1 channel or its threads
        
        # Check if message is in a thread
        is_in_thread = hasattr(message.channel, 'type') and message.channel.type.name == 'public_thread'
        
        if is_in_thread:
            # If in thread, get parent channel name
            parent_channel = message.channel.parent
            channel_name = parent_channel.name.lower() if hasattr(parent_channel, 'name') else ""
            print(f"HANDLE_MESSAGE: Received message in thread of channel: {channel_name}")
        else:
            # Not in thread, get current channel name
            channel_name = message.channel.name.lower() if hasattr(message.channel, 'name') else ""
            print(f"HANDLE_MESSAGE: Received message in channel: {channel_name}")
        
        # STRICTLY enforce channel restriction to ONLY ai-options-calculator or threads within that channel
        if channel_name != "ai-options-calculator":
            print(f"HANDLE_MESSAGE: Ignoring message in non-approved channel: {channel_name}")
            return None
        
        print(f"HANDLE_MESSAGE: Channel {channel_name} is approved")
        
        # Get raw message content
        content = message.content.strip()
        
        # Check for client mention
        bot_user_id = os.getenv('BOT_USER_ID', '1354551896605589584')
        print(f"HANDLE_MESSAGE: BOT_USER_ID: {bot_user_id}")
        
        # Direct check for mention using string format that Discord uses
        mention_string = f"<@{bot_user_id}>"
        mention_string_alt = f"<@!{bot_user_id}>"  # Discord sometimes adds a ! for user mentions
        
        # Check for any of the mention formats
        has_mention = mention_string in content or mention_string_alt in content
        
        # Alternative check - try to use the client object directly from the message
        try:
            if hasattr(message, 'mentions') and message.mentions:
                for mention in message.mentions:
                    print(f"HANDLE_MESSAGE: Message mentions user ID: {mention.id}")
                    if str(mention.id) == bot_user_id:
                        print("HANDLE_MESSAGE: Bot is directly mentioned in message.mentions!")
                        has_mention = True
        except Exception as e:
            print(f"HANDLE_MESSAGE: Error checking mentions: {e}")
        
        # Debug output all the checks
        print(f"HANDLE_MESSAGE: Message content: {content}")
        print(f"HANDLE_MESSAGE: Looking for mention strings: {mention_string} or {mention_string_alt}")
        print(f"HANDLE_MESSAGE: Contains mention string: {has_mention}")
        
        # STRICT MENTION REQUIREMENT - Only respond when directly mentioned
        # We've removed the debug override that was forcing responses
        
        # Process the message ONLY if mentioned AND in the correct channel
        if has_mention:
            print("HANDLE_MESSAGE: BOT MENTIONED - Processing message!")
            
            # Remove both possible mention formats
            content = content.replace(mention_string, '').replace(mention_string_alt, '').strip()
            
            # Special case for stop loss requests
            if "stop loss" in content.lower() or "recommendation" in content.lower() or "reccomendation" in content.lower():
                print("HANDLE_MESSAGE: DIRECT DETECTION - Stop loss or recommendation keywords found in message")
                # Force stop_loss type regardless of NLP result
                forced_stop_loss = True
            else:
                forced_stop_loss = False
                
            # Parse the query
            info = self.nlp.parse_query(content)
            print(f"HANDLE_MESSAGE: Parsed query result: {info}")
            
            # Override the request type if forced_stop_loss is True
            if forced_stop_loss:
                print("HANDLE_MESSAGE: FORCING request_type to stop_loss based on direct keyword detection")
                info['request_type'] = 'stop_loss'
            
            # DEBUGGING: Handle empty request type
            if not info.get('request_type'):
                info['request_type'] = 'unknown'
                print("HANDLE_MESSAGE: Empty request type, setting to 'unknown'")
            
            # Process the request
            try:
                if info['request_type'] == 'option_price':
                    print("HANDLE_MESSAGE: Handling option price request")
                    return await self.handle_option_price_request(message, info)
                elif info['request_type'] == 'stop_loss':
                    print("HANDLE_MESSAGE: Handling stop loss request")
                    return await self.handle_stop_loss_request(message, info)
                elif info['request_type'] == 'unusual_activity':
                    print("HANDLE_MESSAGE: Handling unusual activity request")
                    return await self.handle_unusual_activity_request(message, info)
                else:
                    # Default response for unknown request type
                    print("HANDLE_MESSAGE: Unknown request type, sending default response")
                    default_embed = discord.Embed(
                        title="I'm not sure what you're asking",
                        description=f"I understand requests for options pricing, stop loss recommendations, and unusual options activity. Try one of these example questions:",
                        color=0x3498DB  # Blue color
                    )
                    
                    default_embed.add_field(
                        name="Option Price Estimation",
                        value="What's the price of AAPL $180 calls expiring next Friday?",
                        inline=False
                    )
                    
                    default_embed.add_field(
                        name="Stop Loss Recommendation",
                        value="What's a good stop loss for my TSLA $240 calls expiring Aug 18?",
                        inline=False
                    )
                    
                    default_embed.add_field(
                        name="Unusual Options Activity",
                        value="Show me unusual options activity for MSFT",
                        inline=False
                    )
                    
                    default_embed.add_field(
                        name="Required Parameters for Stop Loss Requests",
                        value="• Ticker symbol (e.g., AAPL, TSLA)\n• Option type (calls or puts)\n• Strike price (e.g., $240)\n• Expiration date (e.g., Aug 18, 2025-06-20)",
                        inline=False
                    )
                    
                    default_embed.set_footer(text="I only respond when directly mentioned in the #blank1 channel or its threads")
                    
                    return default_embed
            except Exception as e:
                print(f"HANDLE_MESSAGE: Error processing request: {e}")
                # Return an error embed
                return discord.Embed(
                    title="Error Processing Request",
                    description=f"An error occurred while processing your request: {str(e)}",
                    color=0xFF0000  # Red for errors
                )
        
        return None
    
    async def handle_option_price_request(self, message, info):
        """Handle requests for option price estimations using Discord embeds for better visual styling"""
        try:
            # Check if we have the minimum required information
            if 'ticker' not in info or not info['ticker']:
                # Create an error embed with clear explanation
                import discord
                missing_embed = discord.Embed(
                    title="Missing Stock Ticker",
                    description="I need a stock ticker symbol to calculate option prices. Please include a stock symbol like AAPL, MSFT, or TSLA in your request.",
                    color=0xFF0000  # Red for errors
                )
                
                # Add example field
                example = "What's the price of AAPL $180 calls expiring next Friday?"
                missing_embed.add_field(
                    name="Example Query:",
                    value=f"*{example}*",
                    inline=False
                )
                
                missing_embed.set_footer(text="For more help, ask 'What can you do?'")
                return missing_embed
            
            ticker = info['ticker']
            
            # Check for option type
            if 'option_type' not in info or not info['option_type']:
                # Create an error embed for missing option type
                import discord
                missing_embed = discord.Embed(
                    title="Missing Option Type",
                    description="Please specify whether you're asking about call options or put options.",
                    color=0xFF0000  # Red for errors
                )
                
                # Add example field
                example = f"What's the price of {ticker} $150 calls expiring next Friday?"
                missing_embed.add_field(
                    name="Example Query:",
                    value=f"*{example}*",
                    inline=False
                )
                
                missing_embed.set_footer(text="For more help, ask 'What can you do?'")
                return missing_embed
            
            # Check for strike price (check both 'strike' and 'strike_price' fields)
            strike_value = None
            if 'strike' in info and info['strike']:
                strike_value = info['strike']
            elif 'strike_price' in info and info['strike_price']:
                strike_value = info['strike_price']
                
            if not strike_value:
                # Create an error embed for missing strike price
                import discord
                missing_embed = discord.Embed(
                    title="Missing Strike Price",
                    description=f"Please specify the strike price for your {ticker} {info['option_type']} option.",
                    color=0xFF0000  # Red for errors
                )
                
                # Add example field
                example = f"What's the price of {ticker} $150 {info['option_type']}s expiring next Friday?"
                missing_embed.add_field(
                    name="Example Query:",
                    value=f"*{example}*",
                    inline=False
                )
                
                missing_embed.set_footer(text="For more help, ask 'What can you do?'")
                return missing_embed
                
            # Assign the strike_value to both fields for consistency
            info['strike'] = strike_value
            info['strike_price'] = strike_value
            
            # Get stock data
            import yfinance as yf
            stock = yf.Ticker(ticker)
            
            # Get available expiration dates
            try:
                expiration_dates = stock.options
                if not expiration_dates:
                    # Create an error embed for no options available
                    import discord
                    error_embed = discord.Embed(
                        title=f"No Options Available",
                        description=f"No options data found for {ticker}.",
                        color=0xFF0000  # Red for errors
                    )
                    error_embed.set_footer(text="Please check the ticker symbol and try again")
                    return error_embed
            except Exception as e:
                # Create an error embed for failure to fetch data
                import discord
                error_embed = discord.Embed(
                    title=f"Error Fetching Option Chain",
                    description=f"Error retrieving options data for {ticker}: {str(e)}",
                    color=0xFF0000  # Red for errors
                )
                error_embed.set_footer(text="Please check your internet connection and try again")
                return error_embed
            
            # Get the expiration date
            selected_expiration = None
            
            # Check for expiration in either field name (expiration or expiration_date)
            expiration_value = None
            if 'expiration' in info and info['expiration']:
                expiration_value = info['expiration']
            elif 'expiration_date' in info and info['expiration_date']:
                expiration_value = info['expiration_date']
                
            if expiration_value:
                # Try to find the closest expiration date from available options
                target_date = expiration_value
                
                # Ensure both fields are populated for consistency
                info['expiration'] = expiration_value
                info['expiration_date'] = expiration_value
                
                # Convert target_date string to datetime object
                try:
                    from datetime import datetime
                    target_datetime = datetime.strptime(target_date, '%Y-%m-%d')
                    
                    # Find the closest expiration date
                    closest_date = None
                    min_difference = float('inf')
                    
                    for exp_date in expiration_dates:
                        exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                        difference = abs((exp_datetime - target_datetime).days)
                        
                        if difference < min_difference:
                            min_difference = difference
                            closest_date = exp_date
                    
                    if closest_date:
                        selected_expiration = closest_date
                except Exception as e:
                    print(f"Error finding closest expiration: {str(e)}")
            
            # If no valid expiration specified, use the next available expiration date
            if not selected_expiration and expiration_dates:
                selected_expiration = expiration_dates[0]
            
            # If we have an expiration date, fetch the option chain
            if selected_expiration:
                try:
                    option_chain = stock.option_chain(selected_expiration)
                    
                    # Get the right chain based on option type
                    if info['option_type'].lower() == 'call':
                        chain = option_chain.calls
                    else:
                        chain = option_chain.puts
                    
                    # Find the option with the closest strike price
                    target_strike = info['strike']
                    closest_option = None
                    min_difference = float('inf')
                    
                    for _, option in chain.iterrows():
                        difference = abs(option['strike'] - target_strike)
                        if difference < min_difference:
                            min_difference = difference
                            closest_option = option
                    
                    # If we found a matching option, create a response
                    if closest_option is not None:
                        # Get current stock price
                        current_price = stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
                        
                        # Create a Discord embed for the response
                        import discord
                        
                        # Choose color based on option type
                        if info['option_type'].lower() == 'call':
                            embed_color = 0x00FF00  # Green for calls
                        else:
                            embed_color = 0xFF0000  # Red for puts
                        
                        embed = discord.Embed(
                            title=f"{ticker} {info['option_type'].upper()} ${closest_option['strike']:.2f} Expiring {selected_expiration}",
                            description=f"**Current Stock Price:** ${current_price:.2f}",
                            color=embed_color
                        )
                        
                        # Add option details
                        embed.add_field(
                            name="Option Details",
                            value=f"**Last Price:** ${closest_option['lastPrice']:.2f}\n"
                                 f"**Bid:** ${closest_option['bid']:.2f}\n"
                                 f"**Ask:** ${closest_option['ask']:.2f}\n"
                                 f"**Volume:** {int(closest_option['volume']) if not np.isnan(closest_option['volume']) else 'N/A'}\n"
                                 f"**Open Interest:** {int(closest_option['openInterest']) if not np.isnan(closest_option['openInterest']) else 'N/A'}",
                            inline=True
                        )
                        
                        # Add option analysis
                        in_the_money = (info['option_type'].lower() == 'call' and current_price > closest_option['strike']) or \
                                      (info['option_type'].lower() == 'put' and current_price < closest_option['strike'])
                        
                        # Calculate moneyness percentage
                        moneyness_pct = abs(current_price - closest_option['strike']) / current_price * 100
                        
                        status = "In the Money 💰" if in_the_money else "Out of the Money 📉"
                        
                        # Calculate break-even price
                        if info['option_type'].lower() == 'call':
                            break_even = closest_option['strike'] + closest_option['lastPrice']
                            break_even_pct = (break_even - current_price) / current_price * 100
                        else:
                            break_even = closest_option['strike'] - closest_option['lastPrice']
                            break_even_pct = (current_price - break_even) / current_price * 100
                        
                        embed.add_field(
                            name="Option Analysis",
                            value=f"**Status:** {status}\n"
                                 f"**Moneyness:** {moneyness_pct:.2f}%\n"
                                 f"**Break-Even:** ${break_even:.2f}\n"
                                 f"**Required Move:** {break_even_pct:.2f}%\n"
                                 f"**Days to Expiry:** {(datetime.strptime(selected_expiration, '%Y-%m-%d') - datetime.now()).days} days",
                            inline=True
                        )
                        
                        # Calculate profit/loss for contract(s)
                        num_contracts = info.get('contracts', 1)
                        contract_cost = closest_option['lastPrice'] * 100 * num_contracts
                        
                        embed.add_field(
                            name=f"Contract Value ({num_contracts} contract{'s' if num_contracts > 1 else ''})",
                            value=f"**Cost:** ${contract_cost:.2f}\n"
                                 f"**Per Contract:** ${closest_option['lastPrice'] * 100:.2f}",
                            inline=False
                        )
                        
                        # Add risk warning 
                        embed.add_field(
                            name="⚠️ Risk Warning",
                            value="Options trading involves substantial risk of loss. This information is for educational purposes only.",
                            inline=False
                        )
                        
                        # Add footer with timestamp
                        from datetime import datetime
                        embed.set_footer(text=f"Data as of {datetime.now().strftime('%Y-%m-%d %H:%M')} | Prices may change quickly during market hours")
                        
                        return embed
                    else:
                        # Create an error embed for option not found
                        import discord
                        error_embed = discord.Embed(
                            title=f"Option Not Found",
                            description=f"No {info['option_type']} option found with strike price ${info['strike']} for {ticker} expiring on {selected_expiration}.",
                            color=0xFF0000  # Red for errors
                        )
                        
                        # Suggest available strikes
                        if not chain.empty:
                            available_strikes = sorted(chain['strike'].unique())[:5]  # Get first 5 strikes
                            strikes_text = '\n'.join([f"${strike:.2f}" for strike in available_strikes])
                            
                            error_embed.add_field(
                                name="Available Strikes (first 5)",
                                value=strikes_text,
                                inline=False
                            )
                            
                            # Show available expirations
                            if len(expiration_dates) > 1:
                                expirations_text = '\n'.join(expiration_dates[:5])  # Show first 5 expiration dates
                                
                                error_embed.add_field(
                                    name="Available Expiration Dates (first 5)",
                                    value=expirations_text,
                                    inline=False
                                )
                        
                        error_embed.set_footer(text="Try again with a different strike price or expiration date")
                        return error_embed
                except Exception as e:
                    # Create an error embed for fetch failure
                    import discord
                    error_embed = discord.Embed(
                        title=f"Error Calculating Option Price",
                        description=f"Error retrieving option data for {ticker} {info['option_type']} ${info['strike']} expiring {selected_expiration}: {str(e)}",
                        color=0xFF0000  # Red for errors
                    )
                    error_embed.set_footer(text="Please check your inputs and try again")
                    return error_embed
            else:
                # Create an error embed for no expiration date
                import discord
                error_embed = discord.Embed(
                    title=f"No Expiration Date Available",
                    description=f"No option expiration dates available for {ticker}.",
                    color=0xFF0000  # Red for errors
                )
                error_embed.set_footer(text="Please check the ticker symbol and try again")
                return error_embed
                
        except Exception as e:
            # Create a generic error embed
            import discord
            error_embed = discord.Embed(
                title="Error Processing Request",
                description=f"An error occurred while processing your request: {str(e)}",
                color=0xFF0000  # Red for errors
            )
            error_embed.set_footer(text="Please try again with a different query")
            return error_embed
    
    async def handle_stop_loss_request(self, message, info):
        """Handle requests for stop loss recommendations using Discord embeds for better visual styling"""
        print("DEBUG: Starting handle_stop_loss_request method")
        print(f"DEBUG: Received info: {info}")
        
        try:
            import discord
            import yfinance as yf
            import numpy as np
            import pandas as pd
            from datetime import datetime, timedelta
            import re
            
            from technical_analysis import get_support_levels, get_stop_loss_recommendations
            from option_calculator import calculate_option_price, get_option_greeks, calculate_theta_decay
            from calculate_dynamic_theta_decay import calculate_dynamic_theta_decay, format_theta_decay_field
            
            # Check if we have the minimum required information
            if 'ticker' not in info or not info['ticker']:
                # Create an error embed with clear explanation
                missing_embed = discord.Embed(
                    title="⚠️ Stock Ticker Required ⚠️",
                    description="I need a stock ticker symbol to calculate stop loss recommendations.\n\nPlease include a stock symbol like AAPL, MSFT, or TSLA in your request.",
                    color=0xFF0000  # Red for errors
                )
                
                # Add example field
                example = "What's a good stop loss for my TSLA $240 calls expiring Aug 18?"
                missing_embed.add_field(
                    name="Example Query:",
                    value=f"*{example}*",
                    inline=False
                )
                
                missing_embed.add_field(
                    name="Required Parameters:",
                    value="• Ticker symbol (e.g., AAPL, TSLA)\n• Option type (calls or puts)\n• Strike price (e.g., $240)\n• Expiration date (e.g., Aug 18, 2025-08-18)",
                    inline=False
                )
                
                missing_embed.set_footer(text="For more help, type '? for help'")
                return missing_embed
            
            # Check for option type
            if 'option_type' not in info or not info['option_type']:
                # Create an error embed for missing option type
                missing_embed = discord.Embed(
                    title="⚠️ Option Type Required ⚠️",
                    description="Please specify whether you're asking about call options or put options for your stop loss recommendation.\n\nThis is required for accurate calculations.",
                    color=0xFF0000  # Red for errors
                )
                
                # Add example field
                example = f"What's a good stop loss for my {info['ticker']} $150 calls expiring Aug 18?"
                missing_embed.add_field(
                    name="Example Query:",
                    value=f"*{example}*",
                    inline=False
                )
                
                missing_embed.add_field(
                    name="Required Parameters:",
                    value="• Ticker symbol (e.g., AAPL, TSLA)\n• Option type (calls or puts)\n• Strike price (e.g., $240)\n• Expiration date (e.g., Aug 18, 2025-08-18)",
                    inline=False
                )
                
                missing_embed.set_footer(text="For more help, type '? for help'")
                return missing_embed
                
            # Check for strike price
            if ('strike' not in info or not info['strike']) and ('strike_price' not in info or not info['strike_price']):
                # Create an error embed for missing strike price
                missing_embed = discord.Embed(
                    title="⚠️ Strike Price Required ⚠️",
                    description=f"Please specify the strike price for your {info['ticker']} {info['option_type']} option.\n\nThe strike price affects the option's value and is critical for stop loss calculations.",
                    color=0xFF0000  # Red for errors
                )
                
                # Add example field
                example = f"What's a good stop loss for my {info['ticker']} $150 {info['option_type']}s expiring Aug 18?"
                missing_embed.add_field(
                    name="Example Query:",
                    value=f"*{example}*",
                    inline=False
                )
                
                missing_embed.add_field(
                    name="Required Parameters:",
                    value="• Ticker symbol (e.g., AAPL, TSLA)\n• Option type (calls or puts)\n• Strike price (e.g., $240)\n• Expiration date (e.g., Aug 18, 2025-08-18)",
                    inline=False
                )
                
                missing_embed.set_footer(text="For more help, type '? for help'")
                return missing_embed
                
            # Check for expiration date
            if ('expiration' not in info or not info['expiration']) and ('expiration_date' not in info or not info['expiration_date']):
                # Create an error embed for missing expiration date
                missing_embed = discord.Embed(
                    title="⚠️ Expiration Date Required ⚠️",
                    description=f"I need the expiration date to calculate accurate stop loss levels for your {info['ticker']} {info['option_type']} option.\n\nExpiration dates significantly impact option pricing and stop loss calculations.",
                    color=0xFF0000  # Red for errors
                )
                
                # Add example field with multiple format examples
                example = f"What's a good stop loss for my {info['ticker']} ${info.get('strike', '150')} {info['option_type']}s expiring Aug 18?"
                example2 = f"What's a good stop loss for my {info['ticker']} ${info.get('strike', '150')} {info['option_type']}s expiring 2025-08-18?"
                
                missing_embed.add_field(
                    name="Example Queries:",
                    value=f"*{example}*\n\n*{example2}*",
                    inline=False
                )
                
                missing_embed.add_field(
                    name="Accepted Date Formats:",
                    value="• Month Day: Aug 18, June 20\n• Month Day, Year: Aug 18, 2025\n• YYYY-MM-DD: 2025-08-18",
                    inline=False
                )
                
                missing_embed.set_footer(text="For more help, type '? for help'")
                return missing_embed
            
            # Extract ticker symbol, strike price, and option type
            ticker_symbol = info.get('ticker', '')
            option_type = info.get('option_type', 'call').lower()
            
            # Extract or calculate strike price
            if 'strike_price' in info:
                strike_price = float(info['strike_price'])
            elif 'strike' in info:
                strike_price = float(info['strike'])
            else:
                strike_price = 0.0
            
            # Get number of contracts
            contracts = info.get('contracts', 1)
            
            # Parse expiration date
            if 'expiration_date' in info and info['expiration_date']:
                expiration_date = info['expiration_date']
                # Check if the expiration date needs parsing
                if isinstance(expiration_date, str):
                    try:
                        # Try to parse with format including day suffix (e.g., "April 12th, 2023")
                        expiration_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', expiration_date)
                        expiration_date = pd.to_datetime(expiration_date)
                    except:
                        try:
                            expiration_date = pd.to_datetime(expiration_date, errors='coerce')
                        except:
                            print(f"Error parsing expiration date: {expiration_date}")
                            expiration_date = datetime.now() + timedelta(days=30)
            else:
                # Use expiration if expiration_date not found
                expiration_date = info.get('expiration', datetime.now() + timedelta(days=30))
                if isinstance(expiration_date, str):
                    try:
                        expiration_date = pd.to_datetime(expiration_date)
                    except:
                        expiration_date = datetime.now() + timedelta(days=30)
            
            # Format the expiration date for display (YYYY-MMM-DD)
            if isinstance(expiration_date, str):
                try:
                    date_obj = pd.to_datetime(expiration_date)
                    month_str = date_obj.strftime('%b').upper()
                    expiration_str = f"{date_obj.year}-{date_obj.month:02d}-{date_obj.day:02d}"
                    formatted_date = f"{date_obj.year}-{date_obj.month:02d}-{date_obj.day:02d}"
                except:
                    expiration_str = expiration_date
                    formatted_date = expiration_date
            else:
                month_str = expiration_date.strftime('%b').upper()
                expiration_str = f"{expiration_date.year}-{expiration_date.month:02d}-{expiration_date.day:02d}"
                formatted_date = f"{expiration_date.year}-{expiration_date.month:02d}-{expiration_date.day:02d}"
            
            # Format the title with stars, dollar sign, and decimal places for the strike price
            formatted_strike = f"${strike_price:.2f}"
            
            # Create the embed with the proper title format and blue sidebar
            embed = discord.Embed(
                title=f"⭐ {ticker_symbol} {option_type.upper()} {formatted_strike} {expiration_str} ⭐",
                description="**📊 STOP LOSS RECOMMENDATION 📊**",
                color=0x368BD6  # Blue color for the sidebar
            )
            
            # Get current stock data
            try:
                stock = yf.Ticker(ticker_symbol)
                current_price = stock.history(period="1d")['Close'].iloc[-1]
            except Exception as e:
                print(f"Error getting stock data: {e}")
                current_price = 0.0  # Default value
                
                # Create an error embed if we can't get the stock data
                error_embed = discord.Embed(
                    title=f"⭐ {ticker_symbol} {option_type.upper()} {formatted_strike} {expiration_str} ⭐",
                    description="**📊 STOP LOSS RECOMMENDATION 📊**",
                    color=0xFF0000  # Red for error
                )
                
                error_embed.add_field(
                    name="⚠️ Error",
                    value="Could not calculate stop loss recommendations due to an error.",
                    inline=False
                )
                
                error_embed.set_footer(text=f"Analysis generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}")
                
                return error_embed
            
            # Calculate days to expiration for theta decay projections
            try:
                if isinstance(expiration_date, str):
                    expiry_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d')
                elif hasattr(expiration_date, 'strftime'):
                    expiry_date_obj = expiration_date
                else:
                    raise ValueError(f"Invalid expiration date format: {expiration_date}")
                
                days_to_expiration = (expiry_date_obj.date() - datetime.now().date()).days
                if days_to_expiration < 0:
                    embed.add_field(
                        name="⚠️ Expiration Warning",
                        value="The provided expiration date appears to be in the past.",
                        inline=False
                    )
                    days_to_expiration = 1  # Default to 1 day remaining when expiration date can't be parsed
                
                # Format expiration date for API call
                expiry_str = expiry_date_obj.strftime('%Y-%m-%d')
            except Exception as e:
                print(f"Error processing expiration date: {e}")
                embed.add_field(
                    name="⚠️ Date Processing Error",
                    value="Could not process the expiration date format. Using only available market data.",
                    inline=False
                )
                expiry_str = expiration_date if isinstance(expiration_date, str) else str(expiration_date)
                days_to_expiration = 1  # Default to 1 day remaining when expiration date can't be parsed
                
            # Try to get option data including price and Greeks
            try:
                option_data = get_option_greeks(stock, expiry_str, strike_price, option_type)
                
                # Check if option_data is None (no data found)
                if option_data is None:
                    embed = discord.Embed(
                        title=f"⚠️ Option Data Not Found ⚠️",
                        description=f"**{ticker_symbol.upper()} {option_type.upper()} ${strike_price} {expiry_str}**\n\nNo data available for this option.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Possible Solutions", value="• Check if the strike price is correct\n• Verify the expiration date format\n• Try a more commonly traded option", inline=False)
                    await message.reply(embed=embed)
                    return embed
                
                # Check if we got an error response instead of actual data
                if option_data.get('data_available') is False:
                    error_msg = option_data.get('error', 'Unable to retrieve market data for this option')
                    embed = discord.Embed(
                        title=f"⚠️ Data Unavailable ⚠️",
                        description=f"**{ticker_symbol.upper()} {option_type.upper()} ${strike_price} {expiry_str}**\n\n{error_msg}",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Possible Solutions", value="• Try a more liquid option\n• Verify the option strike and expiration date\n• Market data may be temporarily unavailable", inline=False)
                    await message.reply(embed=embed)
                    return embed
                
                # Extract option data
                option_price = option_data.get('price', 0.0)
                delta = option_data.get('delta', 0.0)
                theta = option_data.get('theta', 0.0)
                implied_volatility = option_data.get('implied_volatility', 0.0)
                
                # Verify we have valid data
                if option_price <= 0.0:
                    embed = discord.Embed(
                        title=f"⚠️ Invalid Option Price ⚠️",
                        description=f"**{ticker_symbol.upper()} {option_type.upper()} ${strike_price} {expiry_str}**\n\nCannot retrieve a valid price for this option.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Possible Issues", value="• Option may have no market liquidity\n• Strike price may be too far from current price\n• Expiration date may be invalid", inline=False)
                    await message.reply(embed=embed)
                    return embed
                    
            except Exception as e:
                print(f"Error getting option data: {e}")
                # Create an error embed instead of using default values
                embed = discord.Embed(
                    title=f"⚠️ Error Retrieving Option Data ⚠️",
                    description=f"**{ticker_symbol.upper()} {option_type.upper()} ${strike_price} {expiry_str}**\n\nUnable to retrieve market data for this option.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Error Details", value=str(e), inline=False)
                embed.add_field(name="Suggestion", value="Please try again with a different option or later when market data is available.", inline=False)
                await message.reply(embed=embed)
                return embed
            
            # Calculate stop loss level based on technical analysis
            try:
                # Get stop loss recommendations (using formatted expiration date string)
                stop_loss_data = get_stop_loss_recommendations(
                    ticker_symbol, current_price, option_type, expiry_str
                )
                
                # Extract the stop loss level
                stop_loss = stop_loss_data.get("level", current_price * 0.95 if option_type == "call" else current_price * 1.05)
                
                # Enforce buffer limitations based on DTE
                stop_loss = self.enforce_buffer_limits(stop_loss, current_price, option_type, days_to_expiration)
                
                # Extract buffer percentage for display in the output
                # If we can't get from stop_loss_data, calculate from stop_loss and current_price
                if days_to_expiration <= 1:
                    stop_loss_buffer_percentage = 1.0  # 1% for 0-1 DTE
                elif days_to_expiration <= 2:
                    stop_loss_buffer_percentage = 2.0  # 2% for 2 DTE
                elif days_to_expiration <= 5:
                    stop_loss_buffer_percentage = 3.0  # 3% for 3-5 DTE
                else:
                    stop_loss_buffer_percentage = 5.0  # 5% default for longer expirations
                
                # If the buffer wasn't explicitly available, calculate from the stop_loss
                if option_type.lower() == 'call':
                    # For calls, percentage is how far below current price
                    calculated_buffer = abs((stop_loss - current_price) / current_price * 100)
                    # Only use calculated value if we don't have a specific DTE-based value
                    if days_to_expiration > 5:
                        stop_loss_buffer_percentage = calculated_buffer
                else:
                    # For puts, percentage is how far above current price
                    calculated_buffer = abs((stop_loss - current_price) / current_price * 100)
                    # Only use calculated value if we don't have a specific DTE-based value
                    if days_to_expiration > 5:
                        stop_loss_buffer_percentage = calculated_buffer
                
                # Ensure we're using the correct buffer percentage
                if option_type.lower() == 'put':
                    # For puts, always use the fixed buffer percentage based on DTE
                    # so we display 1.0% for 0-1 DTE, 2.0% for 2 DTE, etc.
                    if days_to_expiration <= 1:
                        stop_loss_buffer_percentage = 1.0  # 1% for 0-1 DTE
                    elif days_to_expiration <= 2:
                        stop_loss_buffer_percentage = 2.0  # 2% for 2 DTE
                    elif days_to_expiration <= 5:
                        stop_loss_buffer_percentage = 3.0  # 3% for 3-5 DTE
                    elif days_to_expiration <= 60:
                        stop_loss_buffer_percentage = 5.0  # 5% for medium-term
                    else:
                        stop_loss_buffer_percentage = 7.0  # 7% for long-term
                
                # Calculate option price at stop loss using delta approximation
                # Ensure all values are not None before performing calculations
                if current_price is not None and stop_loss is not None and option_price is not None and delta is not None:
                    price_change = stop_loss - current_price  # Directional change (positive=up, negative=down)
                    
                    # For calls: price goes down when stock goes down; for puts: price goes down when stock goes up
                    if option_type.lower() == 'call':
                        # For calls, negative delta (stock goes down, option loses value)
                        option_price_change = price_change * abs(delta)
                    else:
                        # For puts, negative delta (stock goes up, option loses value)
                        option_price_change = -price_change * abs(delta)
                    
                    option_stop_price = max(0.01, option_price + option_price_change)
                    
                    # Calculate the loss percentage at stop (negative = loss)
                    loss_percentage = (option_stop_price - option_price) / option_price * 100 if option_price > 0 else -64.6
                    # Ensure loss percentage is reasonable (cap at -100% since you can't lose more than 100%)
                    loss_percentage = max(-100, loss_percentage)
                else:
                    # Set default fallback values if any required value is None
                    if current_price is None:
                        print("Warning: current_price is None in stop loss calculation")
                        current_price = stock.history(period='1d')['Close'].iloc[-1] if stock else 0.0
                    
                    if stop_loss is None:
                        print("Warning: stop_loss is None in stop loss calculation")
                        stop_loss = current_price * 0.95 if option_type == "call" else current_price * 1.05
                    
                    if option_price is None:
                        print("Warning: option_price is None in stop loss calculation")
                        option_price = 1.0  # Default fallback
                    
                    if delta is None:
                        print("Warning: delta is None in stop loss calculation")
                        delta = 0.5  # Default fallback
                    
                    # Recalculate with fallback values
                    price_change = stop_loss - current_price  # Directional change
                    
                    # For calls: price goes down when stock goes down; for puts: price goes down when stock goes up
                    if option_type.lower() == 'call':
                        # For calls, negative delta (stock goes down, option loses value)
                        option_price_change = price_change * abs(delta)
                    else:
                        # For puts, negative delta (stock goes up, option loses value)
                        option_price_change = -price_change * abs(delta)
                    
                    option_stop_price = max(0.01, option_price + option_price_change)
                    
                    # Calculate the loss percentage at stop (negative = loss)
                    loss_percentage = (option_stop_price - option_price) / option_price * 100 if option_price > 0 else -64.6
                    # Ensure loss percentage is reasonable (cap at -100% since you can't lose more than 100%)
                    loss_percentage = max(-100, loss_percentage)
                
                # Add all stop loss info in a single field with new formatting
                embed.add_field(
                    name="",
                    value=f"• Current Stock Price: ${current_price:.2f}\n• Current Option Price: ${option_price:.2f}\n• Stock Price Stop Level: ${stop_loss:.2f} ({stop_loss_buffer_percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n• Option Price at Stop Recommendation Level: ${option_stop_price:.2f} (a {abs(loss_percentage):.1f}% loss)",
                    inline=False
                )
                
                # Set color based on option type - green for calls, red for puts
                if option_type.lower() == 'call':
                    embed.color = 0x00FF00  # Green for calls
                else:
                    embed.color = 0xFF0000  # Red for puts
                
                # Add the appropriate trade horizon section based on days to expiration
                if days_to_expiration <= 1:
                    # SCALP trade (very short-term)
                    embed.add_field(
                        name="⚡ SCALP ⚡",
                        value=f"• Scalp trades are generally only meant to be held for 15-30 minutes max due to the quick theta decay",
                        inline=False
                    )
                
                elif days_to_expiration <= 5:
                    # SWING trade (medium-term)
                    embed.add_field(
                        name="📈 SWING TRADE STOP LOSS (4H/Daily chart) 📈",
                        value=f"• Stock Price Stop Level: ${stop_loss:.2f} ({stop_loss_buffer_percentage:.1f}% {'below' if option_type == 'call' else 'above'} current price)\n• Based on stock's volatility (2x ATR)",
                        inline=False
                    )
                
                else:
                    # LONG-TERM trade
                    
                    embed.add_field(
                        name="🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍",
                        value=f"• Ideal For: Options expiring in 3+ months\n• Technical Basis: Major support level with extended volatility buffer\n• Stock Price Stop Level: ${stop_loss:.2f} ({stop_loss_buffer_percentage:.1f}% {'below' if option_type == 'call' else 'above'} current price)\n• Option Price at Stop Recommendation Level: ${option_stop_price:.2f} (a {abs(loss_percentage):.1f}% loss)",
                        inline=False
                    )
                
                # P/L calculations removed as requested
                
                # Options performance message removed as requested
                
                # Add theta decay projection if available
                if days_to_expiration > 0 and theta is not None:
                    # Determine trade horizon based on days to expiration
                    trade_horizon = "auto"  # Will be determined based on days_to_expiration
                    
                    # Calculate dynamic theta decay based on option price, theta, and expiration date
                    decay_data = calculate_dynamic_theta_decay(
                        current_option_price=option_price,
                        theta=theta,
                        expiration_date=expiration_date,
                        trade_horizon=trade_horizon
                    )
                    
                    # Check if we got an error response instead of actual data
                    if decay_data.get('data_available') is False:
                        # Add an error message about theta decay calculation failure
                        embed.add_field(
                            name="⚠️ Theta Decay Projection Unavailable",
                            value="Could not calculate theta decay projections with current market data.",
                            inline=False
                        )
                    else:
                        # Format the field for the embed
                        theta_field = format_theta_decay_field(decay_data)
                        
                        # Add the field to the embed
                        embed.add_field(
                            name=theta_field["name"],
                            value=theta_field["value"],
                            inline=False
                        )
                
                # Add risk warning at the bottom
                embed.add_field(
                    name="⚠️ RISK WARNING ⚠️",
                    value=f"Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                    inline=False
                )
                
            except Exception as e:
                print(f"Error in stop loss calculations: {e}")
                embed.add_field(
                    name="⚠️ Error",
                    value="Could not calculate stop loss recommendations due to an error.",
                    inline=False
                )
            
            # Set the footer with timestamp
            embed.set_footer(text=f"Analysis generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}")
            
            return embed
            
        except Exception as e:
            print(f"Error in handle_stop_loss_request: {e}")
            import traceback
            traceback.print_exc()
            
            # Create an error embed as fallback
            error_embed = discord.Embed(
                title="⚠️ Error Processing Stop Loss Request",
                description="An error occurred while processing your stop loss request.",
                color=0xFF0000  # Red for errors
            )
            
            error_embed.add_field(
                name="Error Details", 
                value=str(e),
                inline=False
            )
            
            error_embed.set_footer(text="Please try again with different parameters or contact support.")
            
            return error_embed
            
    async def show_available_options(self, ticker, stock):
        """Show available options for a stock ticker using Discord embeds for consistent styling"""
        try:
            # Import discord for embeds
            import discord
            from datetime import datetime
            
            # Get available expirations
            expirations = stock.options
            
            if not expirations:
                # Create an error embed for no options available
                error_embed = discord.Embed(
                    title=f"No Options Available",
                    description=f"No options data found for {ticker}.",
                    color=0xFF0000  # Red for errors
                )
                error_embed.set_footer(text="Try a different ticker symbol")
                error_embed.timestamp = datetime.now()
                return error_embed
            
            # Get current stock price
            current_price = stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
            
            # Create the options data embed with teal color for brand consistency
            options_embed = discord.Embed(
                title=f"📈 Options Available for {ticker}",
                description=f"**Current Stock Price:** ${current_price:.2f}",
                color=0x1ABC9C  # Teal for brand consistency
            )
            
            # Create a list of expiration dates
            expiry_text = ""
            # Limit to first 10 expiration dates to avoid too long messages
            for i, expiry in enumerate(expirations[:10]):
                expiry_text += f"• {expiry}\n"
            
            # If there are more expirations, note how many more
            if len(expirations) > 10:
                expiry_text += f"• ... and {len(expirations) - 10} more"
                
            options_embed.add_field(
                name="Available Expiration Dates",
                value=expiry_text,
                inline=False
            )
            
            # Get strikes for the closest expiration date
            closest_expiry = expirations[0]
            
            try:
                option_chain = stock.option_chain(closest_expiry)
                
                # Get strikes for calls
                call_strikes = sorted(option_chain.calls['strike'].unique())
                
                # Get strikes for puts
                put_strikes = sorted(option_chain.puts['strike'].unique())
                
                # Find closest strikes to current price for both calls and puts
                closest_call_strike = min(call_strikes, key=lambda x: abs(x - current_price))
                closest_put_strike = min(put_strikes, key=lambda x: abs(x - current_price))
                
                # Find the ATM call and put prices
                atm_call = option_chain.calls[option_chain.calls['strike'] == closest_call_strike]['lastPrice'].iloc[0]
                atm_put = option_chain.puts[option_chain.puts['strike'] == closest_put_strike]['lastPrice'].iloc[0]
                
                # Add this data to the embed
                options_embed.add_field(
                    name=f"Example - {closest_expiry} (closest to ATM)",
                    value=f"**ATM Call Option:** Strike ${closest_call_strike:.2f} @ ${atm_call:.2f}\n"
                         f"**ATM Put Option:** Strike ${closest_put_strike:.2f} @ ${atm_put:.2f}",
                    inline=False
                )
            except Exception as e:
                options_embed.add_field(
                    name="Strike Price Error",
                    value=f"Could not retrieve strike prices: {str(e)}",
                    inline=False
                )
            
            # Add instructions on how to get more specific data
            options_embed.add_field(
                name="Get Specific Option Details",
                value="To get pricing for a specific option, use:\n"
                     f"*@OptionsBot What's the price of {ticker} $XYZ calls expiring {expirations[0]}?*\n"
                     f"Replace $XYZ with your desired strike price.",
                inline=False
            )
            
            # Add footer
            options_embed.set_footer(text=f"Data as of {datetime.now().strftime('%Y-%m-%d %H:%M')} | Prices may change quickly during market hours")
            options_embed.timestamp = datetime.now()
            
            return options_embed
            
        except Exception as e:
            import discord
            error_embed = discord.Embed(
                title=f"Error Retrieving Options Data",
                description=f"An error occurred while retrieving options data for {ticker}: {str(e)}",
                color=0xFF0000  # Red for errors
            )
            error_embed.set_footer(text="Please try again with a different ticker")
            from datetime import datetime
            error_embed.timestamp = datetime.now()
            return error_embed
    
    async def handle_unusual_activity_request(self, message, info):
        """Handle requests for unusual options activity using Discord embeds for better visual styling"""
        try:
            # Check if we have the minimum required information
            if 'ticker' not in info or not info['ticker']:
                # Create an error embed with clear explanation
                import discord
                missing_embed = discord.Embed(
                    title="Missing Stock Ticker",
                    description="I need a stock ticker symbol to check for unusual options activity. Please include a stock symbol like AAPL, MSFT, or TSLA in your request.",
                    color=0xFF0000  # Red for errors
                )
                
                # Add example field
                example = "Show me unusual options activity for AAPL"
                missing_embed.add_field(
                    name="Example Query:",
                    value=f"*{example}*",
                    inline=False
                )
                
                missing_embed.set_footer(text="For more help, ask 'What can you do?'")
                return missing_embed
            
            ticker = info['ticker']
            
            # Get stock data
            import yfinance as yf
            stock = yf.Ticker(ticker)
            
            # Get basic stock price
            try:
                # Try to get current price from info
                current_price = stock.info.get('currentPrice')
                
                # If that fails, get it from history
                if current_price is None:
                    current_price = stock.history(period='1d')['Close'].iloc[-1]
            except Exception as e:
                print(f"Error getting stock price: {str(e)}")
                # Create an error embed
                import discord
                error_embed = discord.Embed(
                    title="Error Getting Stock Data",
                    description=f"Could not retrieve current price data for {ticker}. Please try again later.",
                    color=0xFF0000  # Red for errors
                )
                error_embed.set_footer(text="This may be due to a network issue or an invalid ticker symbol")
                return error_embed
            
            # Get available expirations
            try:
                expirations = stock.options
                
                if not expirations:
                    # Create an error embed for no options available
                    import discord
                    error_embed = discord.Embed(
                        title=f"No Options Available",
                        description=f"No options data found for {ticker}.",
                        color=0xFF0000  # Red for errors
                    )
                    error_embed.set_footer(text="Try a different ticker symbol")
                    return error_embed
            except Exception as e:
                # Create an error embed
                import discord
                error_embed = discord.Embed(
                    title="Error Getting Options Data",
                    description=f"Could not retrieve options data for {ticker}: {str(e)}",
                    color=0xFF0000  # Red for errors
                )
                error_embed.set_footer(text="This may be due to a network issue or an invalid ticker symbol")
                return error_embed
            
            # Define threshold for unusual activity
            volume_oi_ratio_threshold = 0.5  # Volume should be at least 50% of open interest
            min_volume = 100  # At least 100 contracts traded
            min_open_interest = 50  # At least 50 open interest
            
            unusual_calls = []
            unusual_puts = []
            
            # Check the first 5 expiration dates for unusual activity
            for expiry in expirations[:5]:
                try:
                    option_chain = stock.option_chain(expiry)
                    
                    # Process calls
                    for _, call in option_chain.calls.iterrows():
                        volume = call['volume'] if not np.isnan(call['volume']) else 0
                        open_interest = call['openInterest'] if not np.isnan(call['openInterest']) else 0
                        
                        if volume >= min_volume and open_interest >= min_open_interest and volume / max(1, open_interest) >= volume_oi_ratio_threshold:
                            # Calculate moneyness
                            moneyness = (current_price - call['strike']) / current_price * 100
                            
                            unusual_calls.append({
                                'expiry': expiry,
                                'strike': call['strike'],
                                'volume': volume,
                                'open_interest': open_interest,
                                'volume_oi_ratio': volume / max(1, open_interest),
                                'last_price': call['lastPrice'],
                                'moneyness': moneyness
                            })
                    
                    # Process puts
                    for _, put in option_chain.puts.iterrows():
                        volume = put['volume'] if not np.isnan(put['volume']) else 0
                        open_interest = put['openInterest'] if not np.isnan(put['openInterest']) else 0
                        
                        if volume >= min_volume and open_interest >= min_open_interest and volume / max(1, open_interest) >= volume_oi_ratio_threshold:
                            # Calculate moneyness
                            moneyness = (put['strike'] - current_price) / current_price * 100
                            
                            unusual_puts.append({
                                'expiry': expiry,
                                'strike': put['strike'],
                                'volume': volume,
                                'open_interest': open_interest,
                                'volume_oi_ratio': volume / max(1, open_interest),
                                'last_price': put['lastPrice'],
                                'moneyness': moneyness
                            })
                except Exception as e:
                    print(f"Error processing {expiry} for {ticker}: {str(e)}")
                    continue
            
            # Sort unusual activity by volume/OI ratio in descending order
            unusual_calls = sorted(unusual_calls, key=lambda x: x['volume_oi_ratio'], reverse=True)
            unusual_puts = sorted(unusual_puts, key=lambda x: x['volume_oi_ratio'], reverse=True)
            
            # Create the response embed
            import discord
            
            # Calculate the total flow
            total_call_volume = sum(call['volume'] * call['last_price'] * 100 for call in unusual_calls)
            total_put_volume = sum(put['volume'] * put['last_price'] * 100 for put in unusual_puts)
            
            # Determine if activity is bullish or bearish
            is_bullish = total_call_volume > total_put_volume
            is_bearish = total_put_volume > total_call_volume
            
            # Set color based on sentiment
            if is_bullish:
                embed_color = 0x00FF00  # Green for bullish
            elif is_bearish:
                embed_color = 0xFF0000  # Red for bearish
            else:
                embed_color = 0x808080  # Grey for neutral
            
            # Find largest flow
            largest_flow = 0
            largest_flow_details = ""
            
            if unusual_calls and is_bullish:
                # Find largest call dollars
                largest_call = max(unusual_calls, key=lambda x: x['volume'] * x['last_price'] * 100)
                largest_flow = largest_call['volume'] * largest_call['last_price'] * 100
                strike = largest_call['strike']
                expiry = largest_call['expiry']
                largest_flow_details = f"bet with in-the-money (${strike:.2f}) options expiring on {expiry}."
            elif unusual_puts and not is_bullish:
                # Find largest put dollars
                largest_put = max(unusual_puts, key=lambda x: x['volume'] * x['last_price'] * 100)
                largest_flow = largest_put['volume'] * largest_put['last_price'] * 100
                strike = largest_put['strike']
                expiry = largest_put['expiry']
                largest_flow_details = f"bet with in-the-money (${strike:.2f}) options expiring on {expiry}."
            
            # Calculate percentages
            total_volume = max(1, total_call_volume + total_put_volume)  # Avoid division by zero
            call_percentage = total_call_volume / total_volume * 100
            put_percentage = total_put_volume / total_volume * 100
            
            # Create main content
            main_content = ""
            if largest_flow > 0:
                main_content += f"I'm seeing strongly {'bullish' if is_bullish else 'bearish'} activity for {ticker}, Inc.. The largest flow is a **${largest_flow/1000000:.1f} million {'bullish' if is_bullish else 'bearish'}** {largest_flow_details}\n\n"
                
                # Add institutional flow info
                main_content += f"Institutional Investors are positioning for {'gains' if is_bullish else 'losses'} with {'call' if is_bullish else 'put'} options volume {(call_percentage/put_percentage if is_bullish else put_percentage/call_percentage):.1f}x the open interest.\n\n"
                
                # Add overall flow summary
                main_content += f"**Overall flow:** {int(call_percentage)}% bullish / {int(put_percentage)}% bearish\n\n"
                
                # Add timestamp
                from datetime import datetime
                main_content += f"Based on real-time trading data. Significant volume increases may indicate institutional positioning. • {datetime.now().strftime('%m/%d/%y, %I:%M%p')}"
            else:
                main_content = f"No significant unusual options activity detected for {ticker} in the recent expiration dates."
            
            # Create embed with title and color based on sentiment
            embed = discord.Embed(
                title=f"📊 {ticker} Unusual Options Activity 📊",
                description=main_content,  # Now directly using the content without the redundant header
                color=embed_color
            )
            
            # We don't need additional fields as the screenshot shows all content in the main description
            
            # Add footer with timestamp (but minimal to match screenshot)
            from datetime import datetime
            embed.set_footer(text=f"Data as of {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            embed.timestamp = datetime.now()
            
            print("DEBUG: About to return embed")
            return embed
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in unusual activity request: {str(e)}")
            print(f"Full traceback:\n{error_details}")
            
            # Create a generic error embed
            import discord
            error_embed = discord.Embed(
                title="Error Processing Request",
                description=f"An error occurred while processing your unusual activity request: {str(e)}",
                color=0xFF0000  # Red for errors
            )
            error_embed.set_footer(text="Please try again with a different query")
            return error_embed

# Set up the Discord client
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable the members privileged intent
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)
options_bot = OptionsBot()

@client.event
async def on_ready():
    """Event handler for when the bot is ready"""
    print(f'We have logged in as {client.user}')
    print(f'Bot is connected to {len(client.guilds)} servers')
    
    # Set the bot's activity
    activity = discord.Activity(type=discord.ActivityType.watching, name="option chains | @me for help")
    await client.change_presence(activity=activity)

@client.event
async def on_message(message):
    """Event handler for incoming messages"""
    # Enhanced debug for each message received
    print(f"MSG RECEIVED: '{message.content}' from {message.author}")
    
    # Ignore messages from the bot itself
    if message.author == client.user:
        print("Message is from self, ignoring")
        return
    
    # Debug for checking mentions
    bot_user_id = os.getenv('BOT_USER_ID', '1354551896605589584')
    mention_string = f"<@{bot_user_id}>"
    print(f"Looking for mention: '{mention_string}' in '{message.content}'")
    print(f"Direct check: {mention_string in message.content}")
    
    # Alternative mention check using built-in Discord methods
    if client.user.mentioned_in(message):
        print("BOT IS MENTIONED using Discord's built-in mentioned_in method!")
    else:
        print("Bot is NOT mentioned according to Discord's built-in method")
    
    # Process message through the options bot
    print("Passing to options_bot.handle_message")
    response = await options_bot.handle_message(message)
    
    # Debug response
    print(f"Response from options_bot: {response}")
    
    # If there's a response, send it
    if response:
        print("Sending response")
        # Check if response is a string (legacy) or an embed
        if isinstance(response, str):
            await message.reply(response)
        else:
            # It's an embed
            await message.reply(embed=response)
    else:
        print("No response to send")

@bot.command(name='options_help')
async def options_help_command(ctx):
    """Display help information about the bot using Discord embeds"""
    help_text = options_bot.get_help_instructions()
    
    embed = discord.Embed(
        title="Options Bot Help",
        description=help_text,
        color=0x3498DB  # Blue color
    )
    
    embed.set_footer(text="For more detailed examples, please see the documentation")
    
    await ctx.send(embed=embed)

# Run the bot
def run_discord_bot():
    """Run the Discord bot with the token from environment variables"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        return
    
    client.run(token)

if __name__ == "__main__":
    run_discord_bot()