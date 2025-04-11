"""
Direct fix for incorrect stop level display.
This script specifically targets the issue where the max buffer level is 
being used instead of the technical level in certain responses.
"""

import re

def fix_stop_level_display():
    """Apply a direct fix to handle_stop_loss_request method to ensure the correct stop level is displayed"""
    
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Find the function definition
    handle_stop_loss_request_pattern = r'async def handle_stop_loss_request\(self, message, info\):(.*?)async def [a-zA-Z_]+\('
    match = re.search(handle_stop_loss_request_pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find handle_stop_loss_request method")
        return
    
    method_code = match.group(1)
    
    # Find the enforce_buffer_limits call and the surrounding code for processing the result
    process_pattern = r'(adjusted_stop_loss, max_buffer, buffer_enforced = self\.enforce_buffer_limits\(.*?\).*?)(# Calculate option price at stop loss)'
    process_match = re.search(process_pattern, method_code, re.DOTALL)
    
    if not process_match:
        print("Could not find buffer enforcement processing code")
        return
    
    enforcement_code = process_match.group(1)
    print("Found buffer enforcement processing code:")
    print("=" * 50)
    print(enforcement_code)
    print("=" * 50)
    
    # Check how stop_loss is assigned after enforcement
    if "stop_loss = technical_stop" not in enforcement_code and "stop_loss = adapter_result" in enforcement_code:
        print("ISSUE IDENTIFIED: stop_loss is being assigned from adapter_result incorrectly")
        print("This is happening before enforcement checks, causing the technical level to be lost")
        
    # Look for where we set the displayed stop loss value
    embed_add_field_pattern = r'embed\.add_field\(\s*name="",\s*value=f".*?Stock Price Stop Level: \${(.*?):.2f} \({(.*?):.1f}%'
    embed_match = re.search(embed_add_field_pattern, method_code)
    
    if embed_match:
        stop_var_name = embed_match.group(1)
        stop_pct_var_name = embed_match.group(2)
        print(f"Display shows stop_loss variable: {stop_var_name}")
        print(f"Display shows percentage variable: {stop_pct_var_name}")
    
    # Generate the fix
    fixed_content = content
    
    # Pattern for the problematic code section
    # This is the section where we get the technical level but then immediately overwrite it
    problem_pattern = r'(# Get the technical level and its percentage.*?stop_loss = adapter_result\["level"\].*?)(\n\s*# Calculate max buffer stop based on days to expiration)'
    fix = r'\1\n\n                # Save the technical level for use when no enforcement is needed\n                technical_stop = stop_loss\n\2'
    
    if re.search(problem_pattern, content, re.DOTALL):
        fixed_content = re.sub(problem_pattern, fix, content, flags=re.DOTALL)
        print("Applied fix to preserve technical_stop")
    else:
        print("Could not locate the exact pattern to fix")
    
    # Fix the enforcement decision to use the correct value for comparison
    enforce_check_pattern = r'(adjusted_stop_loss, max_buffer, buffer_enforced = self\.enforce_buffer_limits\()(.*?)(\))'
    
    if re.search(enforce_check_pattern, fixed_content):
        enforce_params = re.search(enforce_check_pattern, fixed_content).group(2)
        if 'stop_loss' in enforce_params:
            # Replace stop_loss with technical_stop in the enforce_buffer_limits call
            fixed_enforce_call = re.sub(r'(enforce_buffer_limits\()stop_loss', r'\1technical_stop', fixed_content)
            fixed_content = fixed_enforce_call
            print("Fixed enforce_buffer_limits call to use technical_stop instead of stop_loss")
    
    # Fix the after-enforcement decision
    after_enforce_pattern = r'(if buffer_enforced:.*?stop_loss = adjusted_stop_loss.*?)(else:.*?)'
    if re.search(after_enforce_pattern, fixed_content, re.DOTALL):
        fixed_after_enforce = re.sub(after_enforce_pattern, r'\1else:\n                    # No enforcement needed, use the technical level\n                    stop_loss = technical_stop  # Restore original technical level\n                    ', fixed_content, flags=re.DOTALL)
        fixed_content = fixed_after_enforce
        print("Fixed after-enforcement code to restore technical level when no enforcement needed")
    
    # Write the fixed content
    with open('fixed_discord_bot.py', 'w') as file:
        file.write(fixed_content)
    
    print("\nDirect fix applied to fixed_discord_bot.py")
    print("This fix ensures the technical level identified by technical analysis is preserved")
    print("and used when buffer enforcement is not needed.")

if __name__ == "__main__":
    fix_stop_level_display()