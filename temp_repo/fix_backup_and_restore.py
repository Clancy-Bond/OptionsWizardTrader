"""
This script backs up the current discord_bot.py file and then attempts to fix the indentation issues
by using the discord_bot.py.bak file as a reference, which is an earlier working version.
"""

import shutil
import os

def backup_and_fix():
    """Backup the current file and restore from the backup to fix indentation"""
    try:
        # Make a backup of the current file
        shutil.copy('discord_bot.py', 'discord_bot.py.broken')
        print("Created backup: discord_bot.py.broken")
        
        # Use the existing backup file as a replacement
        if os.path.exists('discord_bot.py.bak'):
            shutil.copy('discord_bot.py.bak', 'discord_bot.py')
            print("Restored from discord_bot.py.bak")
            return True
        elif os.path.exists('discord_bot.py.fixed'):
            shutil.copy('discord_bot.py.fixed', 'discord_bot.py')
            print("Restored from discord_bot.py.fixed")
            return True
        elif os.path.exists('discord_bot.py.swing_fix'):
            shutil.copy('discord_bot.py.swing_fix', 'discord_bot.py')
            print("Restored from discord_bot.py.swing_fix")
            return True
        else:
            print("No backup files found to restore from")
            return False
    except Exception as e:
        print(f"Error during backup and restore: {e}")
        return False

if __name__ == "__main__":
    backup_and_fix()