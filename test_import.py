#!/usr/bin/env python
"""
Test imports from institutional_sentiment
"""

try:
    from institutional_sentiment import analyze_institutional_sentiment, get_human_readable_summary
    print('Import successful')
except Exception as e:
    print(f'Import error: {e}')