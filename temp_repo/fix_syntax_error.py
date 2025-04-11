"""
Fix the syntax error in discord_bot.py where there's missing whitespace and return statement merging with the next method.
"""

def fix_syntax_error():
    """
    Fix the syntax error in discord_bot.py
    """
    try:
        with open('discord_bot.py', 'r') as f:
            lines = f.readlines()
        
        # Find the line with the error
        for i in range(len(lines)):
            if 'return error_embed' in lines[i] and 'async def show_available_options' in lines[i]:
                # This line has a syntax error - the return statement is merged with the next method
                parts = lines[i].split('async def')
                if len(parts) == 2:
                    # Fix by splitting into two lines
                    lines[i] = parts[0] + '\n\n    async def' + parts[1]
                break
        
        # Write the fixed content back to the file
        with open('discord_bot.py', 'w') as f:
            f.writelines(lines)
        
        print("Successfully fixed syntax error in discord_bot.py")
        return True
        
    except Exception as e:
        print(f"Error fixing syntax error: {e}")
        return False

if __name__ == "__main__":
    fix_syntax_error()