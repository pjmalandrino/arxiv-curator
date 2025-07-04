#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import get_db
from src.core.models import Paper, Summary

def main():
    with get_db() as db:
        # Get counts
        total_papers = db.query(Paper).count()
        papers_with_summaries = db.query(Paper).join(Summary).count()

        print(f"\n📊 Database Statistics:")
        print(f"   Total papers: {total_papers}")
        print(f"   Papers with summaries: {papers_with_summaries}")
        print(f"   Papers without summaries: {total_papers - papers_with_summaries}")

        # Get recent papers
        papers = db.query(Paper).order_by(Paper.published_date.desc()).limit(5).all()

        if papers:
            print(f"\n📄 Recent Papers (showing {len(papers)} of {total_papers}):")
            print("=" * 80)

            for i, paper in enumerate(papers, 1):
                print(f"\n{i}. {paper.title[:80]}...")
                print(f"   ArXiv ID: {paper.arxiv_id}")
                print(f"   Published: {paper.published_date}")

                # Check if paper has summary
                summary = db.query(Summary).filter(Summary.paper_id == paper.id).first()
                if summary:
                    print(f"   ✅ Has summary (Relevance: {summary.relevance_score}/10)")
                else:
                    print(f"   ⚠️  No summary yet")
        else:
            print("\n📭 No papers found in database")

if __name__ == "__main__":
    main()
