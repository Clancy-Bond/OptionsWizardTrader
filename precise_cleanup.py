#!/usr/bin/env python3
"""
Script to perform precise line-by-line cleanup of polygon_integration.py
"""

def cleanup_file():
    """Fix formatting issues with line-specific replacements"""
    with open('polygon_integration.py', 'r') as file:
        lines = file.readlines()
    
    # Lines that need updates (1-indexed)
    updates = {
        # Line 1039: Non-timestamp bullish case needs bolding
        1039: '                summary += f"• I\'m seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bullish**\\n"\n',
        
        # Line 1058: Fallback bullish case needs bolding
        1058: '                summary += f"• I\'m seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bullish**\\n"\n',
        
        # Line 1095: Non-timestamp bearish case needs bolding
        1095: '                summary += f"• I\'m seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bearish**\\n"\n',
        
        # Line 1114: Fallback bearish case needs bolding
        1114: '                summary += f"• I\'m seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bearish**\\n"\n'
    }
    
    # Apply the updates
    for line_number, new_content in updates.items():
        # Adjust for 0-indexed array
        if 0 <= line_number - 1 < len(lines):
            lines[line_number - 1] = new_content
    
    # Write the updated content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.writelines(lines)
    
    print("Applied precise line-by-line cleanup to polygon_integration.py")

if __name__ == "__main__":
    cleanup_file()