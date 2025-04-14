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

# Essential directories to keep
ESSENTIAL_DIRS = [
    "pages",
    "utils"
]

# Pattern prefixes to ALWAYS keep regardless of name
KEEP_PREFIXES = [
    # None for now - we'll keep files by exact name
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
    "clean_"       # Cleanup scripts
]

def should_keep_file(filename):
    """Determine if a file should be kept"""
    # Always keep essential files
    if filename in ESSENTIAL_FILES:
        return True
        
    # Always keep files with essential prefixes
    if any(filename.startswith(prefix) for prefix in KEEP_PREFIXES):
        return True
        
    # Delete files matching patterns to delete
    if any(pattern in filename for pattern in DELETE_PATTERNS):
        return False
        
    # Keep all files in pages and utils directories
    if "/" in filename and filename.split("/")[0] in ESSENTIAL_DIRS:
        return True
        
    # By default, don't keep the file (strict cleanup)
    return False

def cleanup_project():
    """Remove unnecessary files while keeping essential functionality"""
    # List all files and directories
    all_files = []
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in root:
            continue
            
        for file in files:
            # Get relative path
            rel_path = os.path.join(root, file).lstrip('./')
            if rel_path.startswith('/'):
                rel_path = rel_path[1:]
            all_files.append(rel_path)
    
    # Identify files to delete
    files_to_delete = []
    for filename in all_files:
        if not should_keep_file(filename):
            files_to_delete.append(filename)
    
    # Print summary before deletion
    print(f"Found {len(all_files)} total files")
    print(f"Keeping {len(all_files) - len(files_to_delete)} essential files")
    print(f"Will delete {len(files_to_delete)} unnecessary files")
    
    # Ask for confirmation
    print("\nFiles that will be deleted:")
    for filename in sorted(files_to_delete):
        print(f"  - {filename}")
    
    confirmation = input("\nAre you sure you want to delete these files? (yes/no): ")
    if confirmation.lower() != 'yes':
        print("Cleanup cancelled")
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
    cleanup_project()