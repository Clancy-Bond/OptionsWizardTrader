"""
Simple test to verify risk warning formatting in the handle_stop_loss_request method.
"""

import re
import os

def count_risk_warnings():
    """Count risk warning fields in handle_stop_loss_request."""
    try:
        # Read the discord_bot.py file
        with open('discord_bot.py', 'r') as f:
            content = f.read()
        
        # Define the pattern to match the entire handle_stop_loss_request method
        method_pattern = r'async def handle_stop_loss_request\(self, message, info\):.*?(?=async def|$)'
        
        # Find the method
        match = re.search(method_pattern, content, re.DOTALL)
        if not match:
            print("Error: Could not find handle_stop_loss_request method")
            return
        
        # Get the entire method text
        method_text = match.group(0)
        
        # Count risk warning fields
        risk_warning_count = method_text.count('name="⚠️ RISK WARNING"')
        print(f"Found {risk_warning_count} risk warning field definitions in the method")
        
        # If there's more than one, show their contexts
        if risk_warning_count > 1:
            print("Risk warning contexts:")
            for match in re.finditer(r'add_field\(\s*?name="⚠️ RISK WARNING".*?\)', method_text, re.DOTALL):
                context = method_text[max(0, match.start() - 50):min(len(method_text), match.end() + 50)]
                print(f"---\n{context}\n---")
        
        return risk_warning_count
        
    except Exception as e:
        print(f"Error in count_risk_warnings: {e}")
        return None

if __name__ == "__main__":
    count_risk_warnings()