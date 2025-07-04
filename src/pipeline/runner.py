import logging
from typing import Dict

from src.core.config import settings
from src.core.database import get_db
from src.services.arxiv_service import ArxivService
from src.services.ollama_service import OllamaService
from src.services.paper_service import PaperService

logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self):
        self.arxiv = ArxivService(settings.arxiv_categories, settings.arxiv_keywords)
        self.ollama = OllamaService(settings.ollama_host, settings.ollama_model)
        self.paper_service = PaperService()

    def run(self) -> Dict[str, int]:
        logger.info("Starting ArXiv curation pipeline...")

        papers = self.arxiv.fetch_recent_papers(settings.arxiv_max_results)
        logger.info(f"Fetched {len(papers)} papers from ArXiv")

        stats = {'total': len(papers), 'new': 0, 'skipped': 0, 'errors': 0}

        with get_db() as db:
            for paper_data in papers:
                try:
                    if self.paper_service.exists(db, paper_data['arxiv_id']):
                        stats['skipped'] += 1
                        continue

                    paper = self.paper_service.create(db, paper_data)
                    summary_data = self.ollama.summarize_paper(paper_data)

                    if summary_data:
                        self.paper_service.add_summary(db, paper.id, summary_data)
                        stats['new'] += 1

                except Exception as e:
                    logger.error(f"Error processing paper: {e}")
                    stats['errors'] += 1

        logger.info(f"Pipeline complete: {stats}")
        return stats
