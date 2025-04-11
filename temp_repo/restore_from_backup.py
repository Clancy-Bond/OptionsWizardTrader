#!/usr/bin/env python3
"""
Restoration script to restore files from the before_atr_removal_backup directory.
Run this script if you want to revert changes made to the ATR buffer system.

The ATR (Average True Range) buffers were removed to transition from volatility-based
calculations to percentage-based maximum limits for stop-loss. This provides more
consistent behavior and simplifies the stop-loss rules:

- For CALL options: 1.0% for 0-1 DTE, 2.0% for 2 DTE, 3.0% for 3-5 DTE, 5.0% for 6-60 DTE, 5.0% for 60+ DTE
- For PUT options: 1.0% for 0-1 DTE, 2.0% for 2 DTE, 3.0% for 3-5 DTE, 5.0% for 6-60 DTE, 7.0% for 60+ DTE

Running this script will restore the original ATR-based buffer calculations if needed.
"""
import os
import shutil
import sys

def restore_from_backup():
    """Restore files from the backup directory to their original locations."""
    backup_dir = "before_atr_removal_backup"
    
    # Check if backup directory exists
    if not os.path.exists(backup_dir):
        print(f"Error: Backup directory '{backup_dir}' not found. Cannot restore.")
        return False
    
    # Files to restore
    files_to_restore = [
        "discord_bot.py",
        "technical_analysis.py",
        "enhanced_atr_stop_loss.py",
        "combined_scalp_stop_loss.py",
        "run_bot.py"
    ]
    
    # Directories to restore
    dirs_to_restore = [
        "utils",
        "production_code"
    ]
    
    # Restore individual files
    for file in files_to_restore:
        backup_file = os.path.join(backup_dir, file)
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, file)
                print(f"✓ Restored: {file}")
            except Exception as e:
                print(f"✗ Failed to restore {file}: {str(e)}")
        else:
            print(f"! Warning: Backup for {file} not found, skipping.")
    
    # Restore directories
    for directory in dirs_to_restore:
        backup_dir_path = os.path.join(backup_dir, directory)
        if os.path.exists(backup_dir_path) and os.path.isdir(backup_dir_path):
            try:
                # Remove existing directory if it exists
                if os.path.exists(directory):
                    shutil.rmtree(directory)
                # Copy directory
                shutil.copytree(backup_dir_path, directory)
                print(f"✓ Restored directory: {directory}")
            except Exception as e:
                print(f"✗ Failed to restore directory {directory}: {str(e)}")
        else:
            print(f"! Warning: Backup for directory {directory} not found, skipping.")
    
    print("\nRestore operation completed.")
    print("Please restart any running processes or servers for changes to take effect.")
    return True

if __name__ == "__main__":
    print("Starting restoration from backup...")
    
    # Auto-confirm for non-interactive use
    print("Auto-confirming restoration...")
    restore_from_backup()