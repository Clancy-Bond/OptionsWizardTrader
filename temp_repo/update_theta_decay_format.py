"""
Script to update the theta decay warning format in discord_bot.py.
This script finds and replaces all instances of the old pattern (adding theta decay warnings
as separate fields) with the new pattern (adding them directly to the description).
"""

def main():
    # Read the content of the discord_bot.py file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Define the pattern to look for
    old_pattern_lines = [
        '                            # If we have a significant warning, add it',
        '                            if theta_decay[\'warning_status\']:',
        '                                embed.add_field(',
        '                                    name="⏳ Theta Decay Warning",',
        '                                    value=theta_decay[\'warning_message\'],',
        '                                    inline=False',
        '                                )'
    ]
    
    # Alternative patterns with slight variations
    alt_pattern_1_lines = [
        '                        # If we have a significant warning, add it',
        '                        if theta_decay[\'warning_status\']:',
        '                            embed.add_field(',
        '                                name="⏳ Theta Decay Warning",',
        '                                value=theta_decay[\'warning_message\'],',
        '                                inline=False',
        '                            )'
    ]
    
    alt_pattern_2_lines = [
        '                        # If we have a significant warning, add it as a field to the embed',
        '                        if theta_decay[\'warning_status\']:',
        '                            embed.add_field(',
        '                                name="⏳ Theta Decay Warning",',
        '                                value=theta_decay[\'warning_message\'],',
        '                                inline=False',
        '                            )'
    ]
    
    alt_pattern_3_lines = [
        '                        # If we have a significant warning, add it as an embed field',
        '                        if theta_decay[\'warning_status\']:',
        '                            embed.add_field(',
        '                                name="⏳ Theta Decay Warning",',
        '                                value=theta_decay[\'warning_message\'],',
        '                                inline=False',
        '                            )'
    ]
    
    # Define the replacement pattern
    new_pattern_lines = [
        '                            # If we have a significant warning, add it directly to the description',
        '                            # instead of as a separate field for a more cohesive display',
        '                            if theta_decay[\'warning_status\']:',
        '                                # Add the warning directly to the description for more detailed formatting',
        '                                embed.description += f"\\n\\n{theta_decay[\'warning_message\']}"'
    ]
    
    # Alternative replacements with matching indentation
    alt_replacement_1_lines = [
        '                        # If we have a significant warning, add it directly to the description',
        '                        # instead of as a separate field for a more cohesive display',
        '                        if theta_decay[\'warning_status\']:',
        '                            # Add the warning directly to the description for more detailed formatting',
        '                            embed.description += f"\\n\\n{theta_decay[\'warning_message\']}"'
    ]
    
    alt_replacement_2_lines = [
        '                        # If we have a significant warning, add it directly to the description',
        '                        # instead of as a separate field for a more cohesive display',
        '                        if theta_decay[\'warning_status\']:',
        '                            # Add the warning directly to the description for more detailed formatting',
        '                            embed.description += f"\\n\\n{theta_decay[\'warning_message\']}"'
    ]
    
    alt_replacement_3_lines = [
        '                        # If we have a significant warning, add it directly to the description',
        '                        # instead of as a separate field for a more cohesive display',
        '                        if theta_decay[\'warning_status\']:',
        '                            # Add the warning directly to the description for more detailed formatting',
        '                            embed.description += f"\\n\\n{theta_decay[\'warning_message\']}"'
    ]
    
    # Join the patterns into strings
    old_pattern = '\n'.join(old_pattern_lines)
    alt_pattern_1 = '\n'.join(alt_pattern_1_lines)
    alt_pattern_2 = '\n'.join(alt_pattern_2_lines)
    alt_pattern_3 = '\n'.join(alt_pattern_3_lines)
    
    new_pattern = '\n'.join(new_pattern_lines)
    alt_replacement_1 = '\n'.join(alt_replacement_1_lines)
    alt_replacement_2 = '\n'.join(alt_replacement_2_lines)
    alt_replacement_3 = '\n'.join(alt_replacement_3_lines)
    
    # Count instances before replacement
    count_1 = content.count(old_pattern)
    count_2 = content.count(alt_pattern_1)
    count_3 = content.count(alt_pattern_2)
    count_4 = content.count(alt_pattern_3)
    total_before = count_1 + count_2 + count_3 + count_4
    
    # Make replacements
    content = content.replace(old_pattern, new_pattern)
    content = content.replace(alt_pattern_1, alt_replacement_1)
    content = content.replace(alt_pattern_2, alt_replacement_2)
    content = content.replace(alt_pattern_3, alt_replacement_3)
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    # Count instances after replacement
    updated_content = content
    count_1_after = updated_content.count(old_pattern)
    count_2_after = updated_content.count(alt_pattern_1)
    count_3_after = updated_content.count(alt_pattern_2)
    count_4_after = updated_content.count(alt_pattern_3)
    total_after = count_1_after + count_2_after + count_3_after + count_4_after
    
    print(f"Before: Found {total_before} instances of theta decay warning patterns")
    print(f"After: Found {total_after} instances of theta decay warning patterns")
    print(f"Replaced {total_before - total_after} instances")
    
    if total_after > 0:
        print("Warning: Some instances could not be replaced automatically.")
        print("Please manually check the file for any remaining instances.")
    else:
        print("Success! All identified instances were replaced.")

if __name__ == "__main__":
    main()