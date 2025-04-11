"""
Focused script to add the missing theta decay section to the Discord bot.
"""

def add_theta_decay_section():
    """
    Add the missing theta decay section to handle_stop_loss_request method.
    This specifically focuses on adding the section in the right place.
    """
    print("Adding theta decay section...")
    
    # Read the file
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Identify where to add the theta decay section (before the risk warning at the bottom)
    target_section = "# Add risk warning at the BOTTOM only - no duplicates"
    
    # Create the theta decay section
    theta_decay_section = """                # Add theta decay projections
                if days_to_expiration > 0 and greeks and 'theta' in greeks:
                    theta = float(greeks['theta'])
                    
                    # Create theta decay projection with proper formatting using the actual expiration date
                    theta_expiry_display = expiry_display
                    
                    embed.add_field(
                        name=f"⚠️ THETA DECAY PROJECTION TO {theta_expiry_display} ⚠️",
                        value=f"Your option is projected to decay over the next 5 weeks:",
                        inline=False
                    )
                    
                    # Calculate weekly decay projections
                    today = datetime.now().date()
                    decay_text = ""
                    
                    projected_price = option_price
                    for week in range(1, 6):
                        days = week * 7
                        date = today + timedelta(days=days)
                        
                        # Calculate weekly decay
                        weekly_decay = theta * 7
                        weekly_percentage = (weekly_decay / projected_price) * 100
                        cumulative_percentage = (weekly_decay * week / option_price) * 100
                        
                        projected_price = max(0.01, projected_price + weekly_decay)
                        
                        # Format the date as MM-DD
                        date_str = f"{date.month:02d}-{date.day:02d}"
                        
                        # Using current year
                        current_year = datetime.now().year
                        decay_text += f"Week {week} ({current_year}-{date_str}): ${projected_price:.2f} "
                        decay_text += f"({weekly_percentage:.1f}% weekly, {cumulative_percentage:.1f}% total)\\n"
                    
                    decay_text += "\\nConsider your exit strategy carefully as time decay becomes more significant near expiration."
                    embed.add_field(
                        name="",
                        value=decay_text,
                        inline=False
                    )
                
                """
    
    # Insert the theta decay section right before the risk warning
    updated_content = content.replace(target_section, theta_decay_section + target_section)
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("Theta decay section added!")

if __name__ == "__main__":
    add_theta_decay_section()