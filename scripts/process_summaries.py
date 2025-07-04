#!/usr/bin/env python3
# scripts/process_summaries.py - WORKING VERSION WITHOUT check_connection

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import get_db
from src.core.models import Paper, Summary
from src.core.config import settings
from src.services.ollama_service import OllamaService
from src.services.paper_service import PaperService
import requests

def main():
    print("🔄 Processing summaries for papers...")
    print(f"Model: {settings.ollama_model}")

    # Simple Ollama test - no check_connection method!
    try:
        response = requests.get(f"{settings.ollama_host}/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not running! Run: ollama serve")
            return
    except:
        print("❌ Cannot connect to Ollama! Run: ollama serve")
        return

    print("✅ Ollama is running!")

    # Initialize services
    ollama = OllamaService(settings.ollama_host, settings.ollama_model)
    paper_service = PaperService()

    with get_db() as db:
        # Get ONE paper without summary
        paper = db.query(Paper).outerjoin(Summary).filter(Summary.id == None).first()

        if not paper:
            print("✅ All papers already have summaries!")
            return

        print(f"\n📄 Processing: {paper.title[:60]}...")

        paper_data = {
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'arxiv_id': paper.arxiv_id,
            'categories': paper.categories
        }

        try:
            summary_data = ollama.summarize_paper(paper_data)

            if summary_data:
                paper_service.add_summary(db, paper.id, summary_data)
                print(f"✅ Success! Relevance: {summary_data['relevance_score']}/10")
                print(f"Summary: {summary_data['summary'][:150]}...")

                # Show progress
                total = db.query(Paper).count()
                with_summaries = db.query(Paper).join(Summary).count()
                print(f"\n📊 Progress: {with_summaries}/{total} papers have summaries")
            else:
                print("❌ Failed to generate summary")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()