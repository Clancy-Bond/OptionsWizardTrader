"""
Fix indentation in discord_bot.py
"""

def fix_indentation():
    """Fix the indentation error in handle_stop_loss_request"""
    try:
        # Read the file
        with open('discord_bot.py', 'r') as f:
            lines = f.readlines()
        
        # Find the line with the method signature
        for i, line in enumerate(lines):
            if line.strip() == "async def handle_stop_loss_request(self, message, info):":
                # Check the next line
                if '"""Handle requests for stop loss recommendations' in lines[i+1]:
                    # Fix the indentation by adding spaces
                    lines[i+1] = "        " + lines[i+1].lstrip()
                    break
        
        # Write the fixed content back to the file
        with open('discord_bot.py', 'w') as f:
            f.writelines(lines)
        
        print("Successfully fixed indentation in handle_stop_loss_request")
        
    except Exception as e:
        print(f"Error fixing indentation: {e}")

if __name__ == "__main__":
    fix_indentation()