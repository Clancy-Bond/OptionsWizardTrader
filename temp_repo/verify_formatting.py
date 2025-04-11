"""
Simple script to verify the formatting of our key elements.
This script will print out the key parts of our code to verify the formatting changes were made correctly.
"""

import re

def verify_formatting():
    """Verify the key formatting elements in discord_bot.py"""
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Check theta decay formatting
    theta_pattern = re.compile(r'name=f"⚠️ THETA DECAY PROJECTION TO.*"')
    theta_matches = theta_pattern.findall(content)
    print("THETA DECAY FORMAT:")
    for match in theta_matches:
        print(f"  {match}")
    
    # Check trade horizon formatting
    horizons = [
        (re.compile(r'name=f"🔍 LONG-TERM STOP LOSS.*"'), "LONG-TERM"),
        (re.compile(r'name=f"📈 SWING TRADE STOP LOSS.*"'), "SWING"),
        (re.compile(r'name=f"⚡ SCALP TRADE STOP LOSS.*"'), "SCALP")
    ]
    
    print("\nTRADE HORIZON FORMATS:")
    for pattern, name in horizons:
        matches = pattern.findall(content)
        for match in matches:
            print(f"  {name}: {match}")
    
    # Check risk warning
    risk_pattern = re.compile(r'name="⚠️ RISK WARNING"')
    risk_matches = list(re.finditer(risk_pattern, content))
    print(f"\nRISK WARNING COUNT: {len(risk_matches)}")
    for i, match in enumerate(risk_matches):
        # Get a bit of context around the match
        start = max(0, match.start() - 50)
        end = min(len(content), match.end() + 50)
        context = content[start:end].replace('\n', ' ')
        print(f"  {i+1}: ...{context}...")

if __name__ == "__main__":
    verify_formatting()