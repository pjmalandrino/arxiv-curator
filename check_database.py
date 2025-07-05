#!/usr/bin/env python3
"""Check the scored papers in the database."""

import sys
sys.path.insert(0, '/Users/pjmalandrino/Documents/Pro/workspace/poc/arxiv-curator')

from src.database import DatabaseManager
from src.config import Config

def check_database():
    """Check papers and summaries in the database."""
    config = Config()
    db = DatabaseManager(config.database_url)
    
    session = db.get_session()
    try:
        # Get all papers with summaries
        from src.models import Paper, Summary
        
        papers = session.query(Paper).join(Summary).all()
        
        print(f"Found {len(papers)} papers with summaries\n")
        
        for paper in papers:
            summary = paper.summaries[0] if paper.summaries else None
            print(f"📄 {paper.title[:60]}...")
            print(f"   ArXiv ID: {paper.arxiv_id}")
            print(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
            print(f"   Score: {summary.relevance_score:.3f}" if summary and summary.relevance_score else "   Score: N/A")
            print(f"   Summary: {summary.summary[:100]}..." if summary else "   No summary")
            print()
    finally:
        session.close()

if __name__ == "__main__":
    check_database()
