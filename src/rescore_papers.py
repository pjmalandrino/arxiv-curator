"""Utility script to rescore existing papers in the database."""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict

from src.config import Config
from src.database import DatabaseManager
from src.scoring import (
    ScoringConfig,
    create_scorer,
    get_default_config,
    Paper
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaperRescorer:
    def __init__(self, config: Config, scoring_config: ScoringConfig = None):
        self.config = config
        self.scoring_config = scoring_config or get_default_config()
        self.db_manager = DatabaseManager(config.database_url)
        self.scorer = create_scorer(self.scoring_config)
    
    async def rescore_all_papers(self):
        """Rescore all papers in the database."""
        # Get all papers
        papers = self.db_manager.get_all_papers()
        logger.info(f"Found {len(papers)} papers to rescore")
        
        # Score each paper
        scored_count = 0
        for paper_record in papers:
            try:
                # Convert to Paper object
                paper = Paper(
                    arxiv_id=paper_record.arxiv_id,
                    title=paper_record.title,
                    abstract=paper_record.abstract,
                    authors=paper_record.authors,
                    categories=paper_record.categories,
                    published_date=paper_record.published_date,
                    pdf_url=paper_record.pdf_url
                )
                
                # Score the paper
                result = await self.scorer.score(paper)
                
                # Save score to database
                self._save_score(paper_record.id, result)
                scored_count += 1
                
                if scored_count % 10 == 0:
                    logger.info(f"Scored {scored_count}/{len(papers)} papers...")
                    
            except Exception as e:
                logger.error(f"Error scoring paper {paper_record.arxiv_id}: {e}")
        
        logger.info(f"Rescoring complete. Scored {scored_count} papers.")
    
    def _save_score(self, paper_id: str, result):
        """Save score to database."""
        # Extract component scores
        components = result.components
        
        score_data = {
            'paper_id': paper_id,
            'total_score': result.score,
            'llm_score': components.get('llm_scorer', {}).get('score'),
            'keyword_score': components.get('keyword_scorer', {}).get('score'),
            'citation_score': components.get('citation_scorer', {}).get('score'),
            'temporal_score': components.get('temporal_scorer', {}).get('score'),
            'author_score': components.get('author_scorer', {}).get('score'),
            'explanation': result.explanation,
            'components': components,
            'metadata': result.metadata
        }
        
        # Save to database (you'd need to implement this method)
        # self.db_manager.save_paper_score(score_data)
        logger.info(f"Score saved for paper {paper_id}: {result.score:.3f}")
    
    async def rescore_recent_papers(self, days: int = 7):
        """Rescore only recent papers."""
        # Implementation would query papers from last N days
        pass


async def main():
    """Main entry point for rescoring."""
    config = Config()
    
    # You can customize the scoring config here
    scoring_config = get_default_config()
    
    rescorer = PaperRescorer(config, scoring_config)
    await rescorer.rescore_all_papers()


if __name__ == "__main__":
    asyncio.run(main())
