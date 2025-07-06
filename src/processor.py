"""
Paper processing pipeline
"""
import logging
import time
from typing import List, Dict, Optional

from src.database import DatabaseManager
from src.arxiv_client import ArxivClient
from src.hf_client import HuggingFaceClient
from src.models import Paper, Summary

logger = logging.getLogger(__name__)


class PaperProcessor:
    """Main paper processing pipeline"""
    
    def __init__(self, db_manager: DatabaseManager, arxiv_client: ArxivClient, hf_client: HuggingFaceClient):
        self.db_manager = db_manager
        self.arxiv_client = arxiv_client
        self.hf_client = hf_client
    
    def process_recent_papers(self, max_papers: int = 50, days_back: int = 7):
        """Process recent papers from ArXiv"""
        logger.info(f"Processing papers from last {days_back} days")
        
        # Fetch papers
        papers = self.arxiv_client.fetch_recent_papers(
            max_results=max_papers,
            days_back=days_back
        )
        
        logger.info(f"Found {len(papers)} papers to process")
        
        # Process each paper
        processed_count = 0
        for paper_data in papers:
            if self.db_manager.paper_exists(paper_data['arxiv_id']):
                logger.info(f"Paper {paper_data['arxiv_id']} already exists, skipping")
                continue
            
            # Save paper
            paper = self.db_manager.save_paper(paper_data)
            if not paper:
                logger.error(f"Failed to save paper {paper_data['arxiv_id']}")
                continue
            
            # Generate summary
            self.summarize_paper(paper.id)
            processed_count += 1
            
            # Rate limiting
            time.sleep(1)
        
        logger.info(f"Processed {processed_count} new papers")
        return processed_count
    
    def summarize_paper(self, paper_id: str):
        """Generate summary for a specific paper"""
        session = self.db_manager.get_session()
        try:
            paper = session.query(Paper).get(paper_id)
            if not paper:
                logger.error(f"Paper {paper_id} not found")
                return None
            
            # Check if summary already exists
            existing_summary = session.query(Summary).filter_by(paper_id=paper_id).first()
            if existing_summary:
                logger.info(f"Summary already exists for paper {paper_id}")
                return existing_summary
            
            # Generate summary
            paper_data = {
                'title': paper.title,
                'authors': paper.authors,
                'abstract': paper.abstract
            }
            
            summary_data = self.hf_client.summarize_paper(paper_data)
            if summary_data:
                return self.db_manager.save_summary(paper_id, summary_data)
            else:
                logger.warning(f"Failed to generate summary for paper {paper_id}")
                return None
                
        finally:
            session.close()
