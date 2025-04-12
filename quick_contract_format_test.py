"""
Quick test of contract formatting
"""
from polygon_integration import get_simplified_unusual_activity_summary

ticker = "TSLA"
summary = get_simplified_unusual_activity_summary(ticker)
print(summary)