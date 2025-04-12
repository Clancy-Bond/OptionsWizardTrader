#!/usr/bin/env python3
"""
Script to clean up duplicate text in polygon_integration.py
"""

def cleanup_file():
    """Fix duplicate 'strongly' and 'Inc.' text"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Fix duplicates
    content = content.replace('strongly strongly', 'strongly')
    content = content.replace(', Inc., Inc.', ', Inc.')
    
    # Make sure the 'million bullish' in non-timestamp case is also bolded
    content = content.replace('${premium_in_millions:.1f} million bullish\nbet', '${premium_in_millions:.1f} **million bullish**\nbet')
    content = content.replace('${premium_in_millions:.1f} million bearish\nbet', '${premium_in_millions:.1f} **million bearish**\nbet')
    
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Cleaned up duplicate text in polygon_integration.py")

if __name__ == "__main__":
    cleanup_file()