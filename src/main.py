import logging
import time
from typing import List, Dict

from src.config import Config
from src.arxiv_client import ArxivClient
from src.hf_client import HuggingFaceClient
from src.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArxivCurationPipeline:
    def __init__(self, config: Config):
        self.config = config
        self.arxiv_client = ArxivClient(config.arxiv_categories, config.arxiv_keywords)
        self.hf_client = HuggingFaceClient(
            model=config.hf_model,
            api_key=config.hf_token
        )
        self.db_manager = DatabaseManager(config.database_url)

    def run(self, days_back: int = 7):
        """Lance le pipeline complet"""
        logger.info("Starting ArXiv curation pipeline...")
        logger.info(f"Using HuggingFace model: {self.config.hf_model}")

        # 1. Récupération des papiers
        papers = self.arxiv_client.fetch_recent_papers(
            max_results=self.config.arxiv_max_results,
            days_back=days_back
        )
        logger.info(f"Fetched {len(papers)} papers from ArXiv")

        # 2. Traitement par batch
        new_papers_count = 0
        for i in range(0, len(papers), self.config.batch_size):
            batch = papers[i:i + self.config.batch_size]

            for paper_data in batch:
                # Vérifier si le papier existe déjà
                if self.db_manager.paper_exists(paper_data['arxiv_id']):
                    logger.info(f"Paper {paper_data['arxiv_id']} already exists, skipping...")
                    continue

                # Sauvegarder le papier
                paper = self.db_manager.save_paper(paper_data)
                if not paper:
                    continue

                # Générer le résumé
                logger.info(f"Generating summary for: {paper.title}")
                summary_data = self.hf_client.summarize_paper(paper_data)

                if summary_data:
                    self.db_manager.save_summary(paper.id, summary_data)
                    new_papers_count += 1

                # Pause pour éviter de surcharger l'API
                time.sleep(2)  # Un peu plus de délai pour l'API HF

        logger.info(f"Pipeline completed. Processed {new_papers_count} new papers.")

def main():
    """Point d'entrée principal"""
    config = Config()
    pipeline = ArxivCurationPipeline(config)

    # Lancer le pipeline
    pipeline.run(days_back=7)

if __name__ == "__main__":
    main()
