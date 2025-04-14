"""
Cleanup script to remove unnecessary files and focus on core functionality:
1. Unusual options activity detection
2. Discord bot for unusual activity reporting
3. Streamlit admin interface for bot management
"""

import os
import shutil

# Essential files to keep (direct matches)
ESSENTIAL_FILES = [
    # Core functionality
    "unusual_activity.py",
    "polygon_integration.py", 
    "polygon_trades.py",
    "discord_bot.py",
    "discord_bot_config.py",
    
    # Streamlit interface
    "main.py",
    "simple_app.py",
    
    # Environment and configuration
    ".env",
    "config.json",
    "discord_permissions.json",
    
    # This cleanup script
    "cleanup_project.py",
    
    # Required system files
    ".replit",
    "replit.nix",
    "pyproject.toml"
]

# Additional specific files to keep
ADDITIONAL_KEEP_FILES = [
    # Add any other specific files here
    "theme_selector.py",
    "polygon_tickers.json",
    "valid_tickers.json",
    "common_words.txt",
    "generated-icon.png"
]

# Essential directories to keep entirely (don't process files within)
ESSENTIAL_DIRS = [
    "pages",
    "utils",
    "attached_assets",
    ".streamlit"
]

# File patterns to always delete
DELETE_PATTERNS = [
    "test_",       # Test scripts
    "fix_",        # Fix scripts 
    "check_",      # Check scripts
    "debug_",      # Debug scripts
    "direct_",     # Direct fix scripts
    ".bak",        # Backup files
    ".backup",     # Backup files
    ".before_",    # Before files
    "verify_",     # Verification scripts
    "update_",     # Update scripts
    "extract_",    # Extract scripts
    "apply_",      # Apply scripts
    "clean_"       # Cleanup scripts (except this one)
]

# System directories to skip completely (don't process)
SKIP_DIRS = [
    ".git",
    "pythonlibs",
    ".upm",
    "__pycache__",
    "temp_repo",
    "venv"
]

def should_keep_file(filename):
    """Determine if a file should be kept"""
    # Always keep essential files
    if filename in ESSENTIAL_FILES or filename in ADDITIONAL_KEEP_FILES:
        return True
        
    # Delete files matching patterns to delete
    if any(pattern in filename for pattern in DELETE_PATTERNS):
        # Special case: don't delete this cleanup script
        if filename == "cleanup_project.py":
            return True
        return False
        
    # Keep all files in essential directories
    for dir_name in ESSENTIAL_DIRS:
        if filename.startswith(f"{dir_name}/") or filename == dir_name:
            return True
        
    # By default, keep the file (safer approach)
    return True

def cleanup_project(confirm=False):
    """Remove unnecessary files while keeping essential functionality"""
    # Get list of files in the root directory only
    root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    # Identify files to delete
    files_to_delete = []
    for filename in root_files:
        if not should_keep_file(filename):
            files_to_delete.append(filename)
    
    # Print summary before deletion
    print(f"Found {len(root_files)} files in the root directory")
    print(f"Will delete {len(files_to_delete)} unnecessary files")
    
    # List files that will be deleted
    print("\nFiles that will be deleted:")
    for filename in sorted(files_to_delete):
        print(f"  - {filename}")
    
    if not confirm:
        print("\nRun with --confirm to execute deletion")
        return
    
    # Delete files
    for filename in files_to_delete:
        try:
            os.remove(filename)
            print(f"Deleted: {filename}")
        except Exception as e:
            print(f"Error deleting {filename}: {str(e)}")
    
    print("\nCleanup complete!")

if __name__ == "__main__":
    import sys
    # Check if --confirm flag is passed
    confirm = "--confirm" in sys.argv
    cleanup_project(confirm)