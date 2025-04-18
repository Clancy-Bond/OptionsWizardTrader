import os
import json
import re
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import option_calculator
import unusual_activity
from datetime import datetime
import utils_file

def load_config():
    """Load configuration from file"""
    with open('config.json', 'r') as f:
        return json.load(f)

class OptionsBotNLP:
    """Natural language processor for options trading queries"""
    
    def __init__(self):
        self.common_words = []
        self.load_common_words()
    
    def load_common_words(self):
        """Load common English words that should be ignored when processing tickers"""
        common_words_path = 'common_words.txt'
        
        try:
            if os.path.exists(common_words_path):
                with open(common_words_path, 'r') as f:
                    self.common_words = [word.strip().upper() for word in f.readlines()]
                print(f"Loaded {len(self.common_words)} common words for ticker filtering")
            else:
                # Create a basic set of common words if file doesn't exist
                self.common_words = ["THE", "AND", "FOR", "PUT", "CALL", "STOCK", "OPTION", "PRICE", 
                                    "TARGET", "GET", "SET", "WHAT", "HOW", "WHY", "WHEN", "WHO", 
                                    "CAN", "COULD", "WOULD", "SHOULD", "MAY", "MIGHT", "WILL", 
                                    "SHALL", "MUST", "HAVE", "HAS", "HAD", "DO", "DOES", "DID", 
                                    "IS", "ARE", "WAS", "WERE", "BE", "BEEN", "BEING", "THIS", 
                                    "THAT", "THESE", "THOSE", "WITH", "FROM", "TO", "AT", "BY", 
                                    "ON", "OFF", "UP", "DOWN", "IN", "OUT", "OVER", "UNDER", 
                                    "AGAIN", "FURTHER", "THEN", "ONCE", "HERE", "THERE", "WHEN", 
                                    "WHERE", "WHY", "HOW", "ALL", "ANY", "BOTH", "EACH", "FEW", 
                                    "MORE", "MOST", "OTHER", "SOME", "SUCH", "NO", "NOR", "NOT", 
                                    "ONLY", "OWN", "SAME", "SO", "THAN", "TOO", "VERY", "JUST", 
                                    "ONE", "FIRST", "TWO", "SECOND", "NEW", "OLD", "HIGH", "LOW"]
                
                # Save the basic set for future use
                with open(common_words_path, 'w') as f:
                    f.write('\n'.join(self.common_words))
                print(f"Created basic list of {len(self.common_words)} common words for filtering")
        except Exception as e:
            print(f"Warning: Could not load common words: {e}")
            # Fallback to a minimal set
            self.common_words = ["THE", "AND", "FOR", "PUT", "CALL", "WHAT", "HOW", "WHY"]
    
    def parse_query(self, query):
        """Parse a natural language query for options trading parameters"""
        query = query.upper()
        
        # Default result structure
        result = {
            'intent': None,
            'ticker': None,
            'target_price': None,
            'expiration': None,
            'strike': None,
            'option_type': None
        }
        
        # Detect basic intents
        if any(phrase in query for phrase in ['PRICE', 'ESTIMATE', 'CALCULATE', 'WORTH', 'VALUE']):
            result['intent'] = 'price'
        elif any(phrase in query for phrase in ['UNUSUAL', 'ACTIVITY', 'VOLUME', 'FLOW']):
            result['intent'] = 'unusual_activity'
            # Check if query is asking for both call and put unusual activity
            if 'BOTH' in query or ('CALL' in query and 'PUT' in query):
                result['intent'] = 'unusual_activity_both'
        
        # Extract ticker symbol
        # First pass: look for standalone words that aren't common words
        words = re.findall(r'\b[A-Z]{1,5}\b', query)
        potential_tickers = [w for w in words if w not in self.common_words and len(w) <= 5]
        
        # Second pass: if first pass found nothing, look for $ prefixed tickers
        if not potential_tickers:
            dollar_tickers = re.findall(r'\$([A-Z]{1,5})\b', query)
            potential_tickers = [t for t in dollar_tickers if t not in self.common_words]
        
        # Validate tickers and use the first valid one found
        for ticker in potential_tickers:
            if utils_file.is_valid_ticker(ticker):
                result['ticker'] = ticker
                break
        
        # Extract option type
        if 'CALL' in query and 'PUT' not in query:
            result['option_type'] = 'call'
        elif 'PUT' in query and 'CALL' not in query:
            result['option_type'] = 'put'
        
        # Extract target price
        price_match = re.search(r'(?:TARGET|PRICE|REACHES?|HITS?)\s+(?:\$?)(\d+(?:\.\d+)?)', query)
        if price_match:
            result['target_price'] = float(price_match.group(1))
        
        # Extract strike price
        strike_match = re.search(r'(?:STRIKE|AT)\s+(?:\$?)(\d+(?:\.\d+)?)', query)
        if strike_match:
            result['strike'] = float(strike_match.group(1))
        
        # Extract expiration date
        exp_date_match = re.search(r'(?:EXPIR(?:Y|ING|ES|ATION)|DATED?)\s+(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)', query)
        if exp_date_match:
            result['expiration'] = exp_date_match.group(1)
        else:
            # Look for date in format YYYY-MM-DD
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', query)
            if date_match:
                result['expiration'] = date_match.group(1)
            else:
                # Handle relative date references
                relative_date = utils_file.parse_relative_date(query.lower())
                if relative_date:
                    result['expiration'] = relative_date
        
        return result

class OptionsBot(commands.Bot):
    """Discord bot for options trading analysis"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.nlp = OptionsBotNLP()
        self.permissions = utils_file.load_permissions()
        
    async def on_ready(self):
        """Called when the bot is ready"""
        print(f"Logged in as {self.user} ({self.user.id})")
        print("------")
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore our own messages
        if message.author == self.user:
            return
        
        # Only respond to mentions of the bot
        if self.user not in message.mentions:
            return
            
        # Execute commands
        await self.process_commands(message)
        
        # Process using NLP
        content = message.content.replace(f'<@{self.user.id}>', '').strip()
        parsed = self.nlp.parse_query(content)
        
        # Check permissions
        if 'channel_whitelist' in self.permissions and str(message.channel.id) not in self.permissions['channel_whitelist']:
            # Check if user is admin and give helpful response
            if 'admin_users' in self.permissions and str(message.author.id) in self.permissions['admin_users']:
                await message.channel.send(f"This channel is not whitelisted. Admins can add it with: `@{self.user.name} add channel`")
            return
            
        # Handle different intents
        if parsed['intent'] == 'price' and parsed['ticker']:
            await self.handle_price_request(message, parsed)
        elif parsed['intent'] == 'unusual_activity' and parsed['ticker']:
            await self.handle_unusual_activity_request(message, parsed)
        elif parsed['intent'] == 'unusual_activity_both' and parsed['ticker']:
            await self.handle_unusual_activity_for_both(message, parsed)
        elif 'add channel' in content.lower() and 'admin_users' in self.permissions and str(message.author.id) in self.permissions['admin_users']:
            # Admin command to add channel to whitelist
            if 'channel_whitelist' not in self.permissions:
                self.permissions['channel_whitelist'] = []
            
            channel_id = str(message.channel.id)
            if channel_id not in self.permissions['channel_whitelist']:
                self.permissions['channel_whitelist'].append(channel_id)
                
                # Save updated permissions
                with open('discord_permissions.json', 'w') as f:
                    json.dump(self.permissions, f, indent=2)
                
                await message.channel.send(f"Added channel to whitelist.")
            else:
                await message.channel.send(f"Channel is already whitelisted.")
        elif parsed['ticker']:
            # If we have a ticker but no recognized intent, provide helpful message
            await message.channel.send(f"I recognized the ticker {parsed['ticker']}, but I'm not sure what to do with it. Try asking about unusual options activity.")
        elif not parsed['ticker'] and any(word in content.lower() for word in ['help', 'how', 'what']):
            # Provide help message
            help_text = ("I can help with options trading analysis. Here's what you can ask me:\n\n"
                        "- Unusual options activity: `@SWJ-AI-Options unusual options for MSFT`\n\n"
                        "Make sure to include a valid ticker symbol in your question.")
            await message.channel.send(help_text)
        else:
            # Fallback for unrecognized queries
            await message.channel.send("I couldn't understand that request. Please include a valid ticker symbol and ask about unusual options activity.")
    
    async def handle_price_request(self, message, parsed):
        """Handle option price estimation requests - currently disabled"""
        await message.channel.send("Option price estimation is currently disabled. Please try the unusual options activity feature instead.")
    

    
    async def handle_unusual_activity_request(self, message, parsed):
        """Handle unusual options activity requests"""
        # Check for minimum required parameters
        if not parsed['ticker']:
            await message.channel.send(f"I need a ticker symbol to check unusual options activity. Try something like: `@{self.user.name} unusual options for AAPL`")
            return
        
        # Set defaults for missing parameters
        if not parsed['option_type']:
            # If not specified, default based on keywords in the message
            content = message.content.lower()
            if 'call' in content and 'put' not in content:
                parsed['option_type'] = 'call'
            elif 'put' in content and 'call' not in content:
                parsed['option_type'] = 'put'
            else:
                # Default to calls if nothing specified
                parsed['option_type'] = 'call'
        
        try:
            # First send a message indicating we're processing the request
            processing_msg = await message.channel.send(f"Processing unusual options activity for {parsed['ticker']}... This may take a moment.")
            
            # Use run_in_executor to run the function in a background thread
            # Always use high-performance mode for Discord bot to ensure faster responses
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(
                None,
                lambda: unusual_activity.get_simplified_unusual_activity_summary(parsed['ticker'], high_performance=True)
            )
            
            # Delete the processing message once we have the results
            try:
                await processing_msg.delete()
            except:
                pass
            
            # Determine what type of response we have
            using_fallback = "not available through our data provider" in response_text.lower()
            no_activity = "no significant unusual options activity" in response_text.lower()
            has_whale_emoji = "🐳" in response_text
            
            if "No unusual options activity" in response_text or "I couldn't get the data" in response_text:
                # Simple plain text response for no data
                await message.channel.send(response_text)
            elif using_fallback:
                # Process the description
                header_end = response_text.find("\n\n")
                if header_end != -1:
                    description = response_text[header_end+2:]
                else:
                    description = response_text
                
                # Data is limited due to API restrictions
                embed = discord.Embed(
                    title=f"📊 {parsed['ticker']} Market Data",
                    description=description,
                    color=discord.Color.blue()  # Blue for informational
                )
                
                embed.set_footer(text="Some premium data requires API plan upgrade. Using basic stock data.")
                
                # Send the embed as a reply to the original message
                await message.reply(embed=embed)
            elif no_activity and not has_whale_emoji:
                # No unusual activity detected
                embed = discord.Embed(
                    title=f"📊 {parsed['ticker']} No Unusual Activity",
                    color=discord.Color.light_gray()  # Grey for neutral
                )
                
                # Process the description
                header_end = response_text.find("\n\n")
                if header_end != -1:
                    description = response_text[header_end+2:]
                else:
                    description = response_text
                    
                embed.description = description
                
                # Send the embed
                await message.channel.send(embed=embed)
            else:
                # Standard unusual activity response with sentiment
                # Check for overall flow percentages to determine color
                import re
                
                # Look for the percentage pattern in overall flow
                # Updated pattern to better match the format "XX% bullish / YY% bearish"
                flow_pattern = r"\*\*Overall flow:\*\*\s*(\d+)%\s*bullish\s*\/?\s*(\d+)%\s*bearish"
                flow_match = re.search(flow_pattern, response_text, re.IGNORECASE)
                print(f"Flow pattern check: '{response_text}' - Match: {flow_match is not None}")
                
                # Try alternate pattern if first one fails (without bold formatting)
                if not flow_match:
                    alt_pattern = r"Overall flow:?\s*(\d+)%\s*bullish\s*\/?\s*(\d+)%\s*bearish"
                    flow_match = re.search(alt_pattern, response_text, re.IGNORECASE)
                    print(f"Alt pattern check: Match: {flow_match is not None}")
                
                # Brute force method if both regex patterns fail
                if not flow_match:
                    # Look for any occurrence of XX% bullish or XX% bearish
                    bullish_pct_pattern = r"(\d+)%\s*bullish"
                    bearish_pct_pattern = r"(\d+)%\s*bearish"
                    
                    bullish_match = re.search(bullish_pct_pattern, response_text, re.IGNORECASE)
                    bearish_match = re.search(bearish_pct_pattern, response_text, re.IGNORECASE)
                    
                    if bullish_match and bearish_match:
                        # Create a mock match object with groups
                        class MockMatch:
                            def __init__(self, bull_pct, bear_pct):
                                self.groups_data = (bull_pct, bear_pct)
                            def group(self, idx):
                                return self.groups_data[idx-1] if idx > 0 else self.groups_data
                                
                        flow_match = MockMatch(bullish_match.group(1), bearish_match.group(1))
                        print(f"Brute force method: Bullish: {bullish_match.group(1)}%, Bearish: {bearish_match.group(1)}%")
                
                if flow_match:
                    # Extract percentages
                    bullish_pct = int(flow_match.group(1))
                    bearish_pct = int(flow_match.group(2))
                    
                    # Set color based on which percentage is higher
                    if bullish_pct > bearish_pct:
                        embed_color = discord.Color.green()  # Green for majority bullish
                    elif bearish_pct > bullish_pct:
                        embed_color = discord.Color.red()  # Red for majority bearish
                    else:
                        embed_color = discord.Color.light_gray()  # Grey for 50-50
                else:
                    # Fallback to keyword detection if percentages not found
                    is_bullish = "bullish" in response_text.lower()
                    is_bearish = "bearish" in response_text.lower()
                    
                    # Set embed color based on sentiment keywords
                    if is_bullish and not is_bearish:
                        embed_color = discord.Color.green()  # Green for bullish
                    elif is_bearish and not is_bullish:
                        embed_color = discord.Color.red()  # Red for bearish
                    else:
                        embed_color = discord.Color.light_gray()  # Grey for neutral or mixed
                
                # Format response text to bold key information
                response_text = response_text.replace("Overall flow:", "**Overall flow:**")
                
                # Bold the dollar amounts with sentiment
                dollar_pattern = r"\$(\d+(?:\.\d+)?)\s+million\s+(bullish|bearish)"
                response_text = re.sub(dollar_pattern, r"**$\1 million \2**", response_text)
                
                # Process the description
                if has_whale_emoji:
                    header_end = response_text.find("\n\n")
                    if header_end != -1:
                        description = response_text[header_end+2:]
                    else:
                        description = response_text
                else:
                    description = response_text
                
                # Format response as Discord embed with whale emoji
                embed = discord.Embed(
                    title=f"🐳 {parsed['ticker']} Unusual Options Activity 🐳",
                    description=description,  # Set in constructor instead of later
                    color=embed_color
                )
                
                # Send the embed message as a reply instead of a new message
                await message.reply(embed=embed)
        except Exception as e:
            await message.channel.send(f"I encountered an error checking unusual options activity: {str(e)}")
    
    async def handle_unusual_activity_for_both(self, message, parsed):
        """Handle unusual options activity requests for both calls and puts"""
        # First send a message indicating we're processing the request
        processing_msg = await message.channel.send(f"Processing unusual options activity for {parsed['ticker']} (both calls & puts)... This may take a moment.")
        
        # Run the intensive operation in a separate thread to prevent blocking the bot
        loop = asyncio.get_event_loop()
        try:
            response_text = await loop.run_in_executor(
                None,
                lambda: unusual_activity.get_simplified_unusual_activity_summary(parsed['ticker'], high_performance=True)
            )
        except Exception as e:
            print(f"Error with Polygon unusual activity summary: {str(e)}")
            response_text = f"📊 Unable to retrieve unusual options activity for {parsed['ticker']} from Polygon.io.\nError: {str(e)}"
        
        # Delete the processing message once we have the results
        try:
            await processing_msg.delete()
        except:
            pass
        
        # Determine what type of response we have
        using_fallback = "not available through our data provider" in response_text.lower()
        no_activity = "no significant unusual options activity" in response_text.lower()
        has_whale_emoji = "🐳" in response_text
        
        if using_fallback:
            # Process the description
            header_end = response_text.find("\n\n")
            if header_end != -1:
                description = response_text[header_end+2:]
            else:
                description = response_text
            
            # Data is limited due to API restrictions
            embed = discord.Embed(
                title=f"📊 {parsed['ticker']} Market Data",
                description=description,
                color=discord.Color.blue()  # Blue for informational
            )
            
            # Since we have unlimited API calls, no need for the upgrade message
            embed.set_footer(text="Using available market data.")
            
        elif no_activity and not has_whale_emoji:
            # Process the description
            header_end = response_text.find("\n\n")
            if header_end != -1:
                description = response_text[header_end+2:]
            else:
                description = response_text
            
            # No unusual activity detected
            embed = discord.Embed(
                title=f"📊 {parsed['ticker']} No Unusual Activity",
                description=description,
                color=discord.Color.light_gray()  # Grey for neutral
            )
            
        else:
            # Standard unusual activity response with sentiment
            # Check for overall flow percentages to determine color
            import re
            
            # Look for the percentage pattern in overall flow
            # Updated pattern to better match the format "XX% bullish / YY% bearish" with bold formatting
            flow_pattern = r"\*\*Overall flow:\*\*\s*(\d+)%\s*bullish\s*\/?\s*(\d+)%\s*bearish"
            flow_match = re.search(flow_pattern, response_text, re.IGNORECASE)
            print(f"Flow pattern check (both): '{response_text}' - Match: {flow_match is not None}")
            
            # Try alternate pattern if first one fails (without bold formatting)
            if not flow_match:
                alt_pattern = r"Overall flow:?\s*(\d+)%\s*bullish\s*\/?\s*(\d+)%\s*bearish"
                flow_match = re.search(alt_pattern, response_text, re.IGNORECASE)
                print(f"Alt pattern check (both): Match: {flow_match is not None}")
            
            # Brute force method if both regex patterns fail
            if not flow_match:
                # Look for any occurrence of XX% bullish or XX% bearish
                bullish_pct_pattern = r"(\d+)%\s*bullish"
                bearish_pct_pattern = r"(\d+)%\s*bearish"
                
                bullish_match = re.search(bullish_pct_pattern, response_text, re.IGNORECASE)
                bearish_match = re.search(bearish_pct_pattern, response_text, re.IGNORECASE)
                
                if bullish_match and bearish_match:
                    # Create a mock match object with groups
                    class MockMatch:
                        def __init__(self, bull_pct, bear_pct):
                            self.groups_data = (bull_pct, bear_pct)
                        def group(self, idx):
                            return self.groups_data[idx-1] if idx > 0 else self.groups_data
                            
                    flow_match = MockMatch(bullish_match.group(1), bearish_match.group(1))
                    print(f"Brute force method (both): Bullish: {bullish_match.group(1)}%, Bearish: {bearish_match.group(1)}%")
            
            if flow_match:
                # Extract percentages
                bullish_pct = int(flow_match.group(1))
                bearish_pct = int(flow_match.group(2))
                
                # Set color based on which percentage is higher
                if bullish_pct > bearish_pct:
                    embed_color = discord.Color.green()  # Green for majority bullish
                elif bearish_pct > bullish_pct:
                    embed_color = discord.Color.red()  # Red for majority bearish
                else:
                    embed_color = discord.Color.light_gray()  # Grey for 50-50
            else:
                # Fallback to keyword detection if percentages not found
                is_bullish = "bullish" in response_text.lower()
                is_bearish = "bearish" in response_text.lower()
                
                # Set embed color based on sentiment keywords
                if is_bullish and not is_bearish:
                    embed_color = discord.Color.green()  # Green for bullish
                elif is_bearish and not is_bullish:
                    embed_color = discord.Color.red()  # Red for bearish
                else:
                    embed_color = discord.Color.light_gray()  # Grey for neutral or mixed
            
            # Format response text to bold key information
            response_text = response_text.replace("Overall flow:", "**Overall flow:**")
            
            # Bold the dollar amounts with sentiment
            dollar_pattern = r"\$(\d+(?:\.\d+)?)\s+million\s+(bullish|bearish)"
            response_text = re.sub(dollar_pattern, r"**$\1 million \2**", response_text)
            
            # Process the description
            if has_whale_emoji:
                header_end = response_text.find("\n\n")
                if header_end != -1:
                    description = response_text[header_end+2:]
                else:
                    description = response_text
            else:
                description = response_text
            
            # Format response as Discord embed with whale emoji
            embed = discord.Embed(
                title=f"🐳 {parsed['ticker']} Unusual Options Activity (Calls & Puts) 🐳",
                description=description,  # Set in constructor instead of later
                color=embed_color
            )
            
        # Send the embed message as a reply instead of a new message
        await message.reply(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN_2")
    if not token:
        print("Error: Neither DISCORD_TOKEN nor DISCORD_TOKEN_2 environment variable is set.")
        exit(1)
    
    bot = OptionsBot()
    bot.run(token)
