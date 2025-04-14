"""
Final fix for the formatting issues in unusual options activity output
"""

import re

def apply_final_format_fix():
    """
    Apply very specific changes to fix the formatting in polygon_integration.py:
    1. Remove 'bet that' and 'occurred at' wording
    2. Change 'X-the-money' to 'in-the-money (X.00)'
    3. Fix expiration date format to MM/DD/YY
    """
    # Read the file
    with open("polygon_integration.py", "r") as file:
        content = file.read()
    
    # Fix pattern for bullish flow, these are the most problematic lines
    old_pattern = r"summary \+= f\"• I'm seeing strongly bullish activity for {ticker}, Inc\.\. The largest flow is a \${premium_in_millions:\.1f} million bullish bet that\\n\"\n\s+summary \+= f\"occurred at {timestamp_str} with \""
    new_pattern = r"summary += f\"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** \"\n        # Format in-the-money with strike price\n        if strike_price:\n            summary += f\"in-the-money ({strike_price}) options \"\n        else:\n            summary += f\"options \""
    
    # Fix pattern for bearish flow (similar structure)
    old_pattern2 = r"summary \+= f\"• I'm seeing strongly bearish activity for {ticker}, Inc\.\. The largest flow is a \${premium_in_millions:\.1f} million bearish bet that\\n\"\n\s+summary \+= f\"occurred at {timestamp_str} with \""
    new_pattern2 = r"summary += f\"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** \"\n        # Format in-the-money with strike price\n        if strike_price:\n            summary += f\"in-the-money ({strike_price}) options \"\n        else:\n            summary += f\"options \""
    
    # Fix expiration date format
    old_date_pattern = r"expiring on {expiry_date}"
    new_date_pattern = r"expiring {expiry_date}"
    
    # Fix X-the-money format and remove bet wording for fallback case
    old_money_pattern = r"\${contract_parts\[0\]} {contract_parts\[1\]}-the-money options"
    new_money_pattern = r"in-the-money (${contract_parts[1]}) options"
    
    # First fix the expiration date format in YYYY-MM-DD to MM/DD/YY
    expiry_pattern = r"expiry_date = contract_parts\[2\]"
    expiry_fix = r"""try:
                # Parse date format and convert to MM/DD/YY
                date_parts = contract_parts[2].split('-')
                if len(date_parts) == 3:
                    year, month, day = date_parts
                    expiry_date = f"{month}/{day}/{year[-2:]}"
                else:
                    expiry_date = contract_parts[2]
            except (IndexError, ValueError):
                expiry_date = contract_parts[2]"""
    
    # Apply fixes
    content = content.replace(old_pattern, new_pattern)
    content = content.replace(old_pattern2, new_pattern2)
    content = content.replace(old_date_pattern, new_date_pattern)
    content = re.sub(old_money_pattern, new_money_pattern, content)
    content = content.replace(expiry_pattern, expiry_fix)
    
    # Final output
    with open("polygon_integration.py", "w") as file:
        file.write(content)
    
    print("Applied final format fixes to polygon_integration.py")

if __name__ == "__main__":
    apply_final_format_fix()