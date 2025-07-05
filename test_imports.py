#!/usr/bin/env python3
"""Test if scoring module imports correctly."""

import sys
sys.path.insert(0, '/Users/pjmalandrino/Documents/Pro/workspace/poc/arxiv-curator')

try:
    from src.scoring.base import Paper, ScoringResult
    print("✓ Successfully imported base classes")
    
    from src.scoring.keyword_scorer import KeywordScorer
    print("✓ Successfully imported KeywordScorer")
    
    from src.scoring.config import get_default_config
    print("✓ Successfully imported config")
    
    from src.scoring import create_scorer
    print("✓ Successfully imported create_scorer")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
