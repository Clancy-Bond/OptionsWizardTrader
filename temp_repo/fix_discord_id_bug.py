"""
This script fixes a bug in the Discord bot where a Discord user ID in a mention
was being incorrectly recognized as a price.

The problem was in the regular expression pattern for prices, which was too general
and would match any sequence of digits, including Discord IDs in mention tags. 
This was causing the bot to misinterpret the Discord ID as a price and then 
using the actual strike price as a target price.
"""

def fix_discord_mention_price_bug():
    """
    Update the price pattern in the Discord bot to avoid matching Discord IDs in mentions
    """
    import re
    
    # Original content with the problematic pattern
    old_patterns = """        # Patterns to extract ticker symbols, prices, dates, strikes, and option types
        self.patterns = {
            'ticker': r'\\b[A-Z]{1,5}\\b',  # Ticker symbols like AAPL, MSFT, etc.
            'price': r'\\$?(\\d+\\.?\\d*)',  # Prices like $150, 150, 150.50"""

    # New content with a more specific price pattern that ignores Discord mentions
    new_patterns = """        # Patterns to extract ticker symbols, prices, dates, strikes, and option types
        self.patterns = {
            'ticker': r'\\b[A-Z]{1,5}\\b',  # Ticker symbols like AAPL, MSFT, etc.
            'price': r'(?<!<@)\\$?(\\d+\\.?\\d*)',  # Prices like $150, 150, 150.50 but not Discord IDs in mention tags"""
    
    # Print the changes
    print(f"To fix the Discord ID bug, replace the following in discord_bot.py:\n")
    print(f"Old pattern:\n{old_patterns}\n")
    print(f"New pattern:\n{new_patterns}\n")
    
    # Also update the extraction code that deals with multiple price matches
    old_extraction = """        # If no explicit target found but we have multiple prices, use the second one as target
        # BUT only if the price is not part of the expiration date 
        elif not info['target_price'] and price_matches and len(price_matches) >= 2:
            if price_matches[1] not in expiration_numbers:  # This is the fix
                info['target_price'] = float(price_matches[1])
                print(f"[NLP] Using second price as target: ${info['target_price']}")
            else:
                print(f"[NLP] Ignoring price match '{price_matches[1]}' as it appears to be part of the expiration date")"""
    
    # Improved extraction code that's more cautious about setting prices and provides better debugging
    new_extraction = """        # If no explicit target found but we have multiple prices, use the second one as target
        # BUT only if the price is not part of the expiration date AND is a reasonable number
        elif not info['target_price'] and price_matches and len(price_matches) >= 2:
            # Sanity check - ignore very large numbers which are likely to be IDs or timestamps 
            # Typical stock prices are < 10,000
            try:
                potential_price = float(price_matches[1])
                if price_matches[1] not in expiration_numbers and potential_price < 10000:
                    info['target_price'] = potential_price
                    print(f"[NLP] Using second price as target: ${info['target_price']}")
                else:
                    if potential_price >= 10000:
                        print(f"[NLP] Ignoring price match '{price_matches[1]}' as it's unusually large")
                    else:
                        print(f"[NLP] Ignoring price match '{price_matches[1]}' as it appears to be part of the expiration date")
            except ValueError:
                print(f"[NLP] Error converting price match '{price_matches[1]}' to a number")"""
    
    print(f"Also update the price extraction code:\n")
    print(f"Old extraction:\n{old_extraction}\n")
    print(f"New extraction:\n{new_extraction}\n")
    
    return {
        "old_pattern": old_patterns,
        "new_pattern": new_patterns,
        "old_extraction": old_extraction,
        "new_extraction": new_extraction
    }

if __name__ == "__main__":
    fix_discord_mention_price_bug()