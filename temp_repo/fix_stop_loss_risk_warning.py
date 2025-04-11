"""
Final fix for placing the risk warning at the end of embeds in stop_loss responses
This rewrites the handle_stop_loss_request method to implement proper field ordering
"""

def fix_stop_loss_risk_warning():
    """
    Update the handle_stop_loss_request method to ensure risk warning is always the last field
    """
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    # Find the handle_stop_loss_request function
    stop_loss_function_start = "    async def handle_stop_loss_request(self, message, info):"
    stop_loss_function_end = "    async def show_available_options(self, ticker, stock):"
    
    start_pos = content.find(stop_loss_function_start)
    end_pos = content.find(stop_loss_function_end, start_pos + 1)
    
    if start_pos == -1 or end_pos == -1:
        print("Error: Couldn't find the handle_stop_loss_request method")
        return
    
    # Extract the function content
    function_content = content[start_pos:end_pos]
    
    # Find the end of the function where we need to ensure risk warning is last
    # Look for code right before the return statement
    return_embed_pos = function_content.find("return embed")
    
    if return_embed_pos == -1:
        print("Error: Couldn't find 'return embed' in handle_stop_loss_request")
        return
    
    # Find where to insert our code - look back from the return statement
    insert_pos = function_content.rfind("\n", 0, return_embed_pos)
    if insert_pos == -1:
        print("Error: Couldn't find insert position before 'return embed'")
        return
    
    # Get the indentation level
    indent = function_content[function_content.rfind("\n", 0, insert_pos) + 1:insert_pos].replace("    # Risk warning will be added at the end", "")
    
    # Create the code to ensure risk warning is at the end
    ensure_risk_warning_code = f"""
{indent}# Ensure risk warning is the very last field
{indent}# Use Discord.py's proper API methods for manipulating fields
{indent}
{indent}# First, collect all fields except risk warning
{indent}non_risk_fields = []
{indent}for field in embed.fields:
{indent}    if not (hasattr(field, 'name') and '⚠️ RISK WARNING' in field.name):
{indent}        non_risk_fields.append(field)
{indent}
{indent}# Clear all fields
{indent}embed.clear_fields()
{indent}
{indent}# Re-add all non-risk warning fields
{indent}for field in non_risk_fields:
{indent}    embed.add_field(name=field.name, value=field.value, inline=field.inline)
{indent}
{indent}# Add risk warning as the final field
{indent}embed.add_field(
{indent}    name="⚠️ RISK WARNING",
{indent}    value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
{indent}    inline=False
{indent})
"""
    
    # Insert the code before return embed
    modified_function = function_content[:insert_pos] + ensure_risk_warning_code + function_content[insert_pos:]
    
    # Replace the function in the full content
    new_content = content[:start_pos] + modified_function + content[end_pos:]
    
    # Remove any direct embed.fields = ... assignments
    if "embed.fields =" in new_content:
        print("Removing direct embed.fields assignments...")
        new_content = new_content.replace("embed.fields = [field for field in embed.fields if '⚠️ RISK WARNING' not in field.name]", 
                                        "# Fixed - Using clear_fields() and add_field() instead of direct assignment")
    
    # Write the modified content back
    with open("discord_bot.py", "w") as file:
        file.write(new_content)
    
    print("Successfully updated handle_stop_loss_request method")

if __name__ == "__main__":
    fix_stop_loss_risk_warning()