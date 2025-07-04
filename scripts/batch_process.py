#!/usr/bin/env python3
# scripts/batch_process.py - Process all papers at once

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import get_db
from src.core.models import Paper, Summary
from src.core.config import settings
from src.services.ollama_service import OllamaService
from src.services.paper_service import PaperService

def main():
    print("🚀 Batch processing all papers without summaries...")
    print(f"Using model: gemma3:4b")

    # Force the model
    settings.ollama_model = "gemma3:4b"

    ollama = OllamaService(settings.ollama_host, "gemma3:4b")
    paper_service = PaperService()

    with get_db() as db:
        # Get all papers without summaries
        papers = db.query(Paper).outerjoin(Summary).filter(Summary.id == None).all()

        if not papers:
            print("✅ All papers already have summaries!")
            return

        print(f"\n📚 Found {len(papers)} papers to process")

        for i, paper in enumerate(papers, 1):
            print(f"\n[{i}/{len(papers)}] {paper.title[:60]}...")

            try:
                summary_data = ollama.summarize_paper({
                    'title': paper.title,
                    'authors': paper.authors,
                    'abstract': paper.abstract,
                    'arxiv_id': paper.arxiv_id,
                    'categories': paper.categories
                })

                if summary_data:
                    paper_service.add_summary(db, paper.id, summary_data)
                    print(f"✅ Score: {summary_data['relevance_score']}/10")
                else:
                    print("❌ Failed")
            except Exception as e:
                print(f"❌ Error: {e}")

            # Progress
            total = db.query(Paper).count()
            done = db.query(Paper).join(Summary).count()
            print(f"Progress: {done}/{total}")

            # Small delay
            if i < len(papers):
                time.sleep(2)

        print("\n🎉 Batch processing complete!")

if __name__ == "__main__":
    main()