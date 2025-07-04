import arxiv
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ArxivClient:
    def __init__(self, categories: List[str], keywords: List[str]):
        self.categories = categories
        self.keywords = keywords

    def build_query(self, days_back: int = 7) -> str:
        """Construit une requête ArXiv pour les papiers récents"""
        category_query = " OR ".join([f"cat:{cat}" for cat in self.categories])
        keyword_query = " OR ".join([f'"{kw}"' for kw in self.keywords])

        return f"({category_query}) AND ({keyword_query})"

    def fetch_recent_papers(self, max_results: int = 50, days_back: int = 7) -> List[Dict]:
        """Récupère les papiers récents depuis ArXiv"""
        query = self.build_query(days_back)

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []
        for result in search.results():
            paper_data = {
                'arxiv_id': result.entry_id.split('/')[-1],
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'published_date': result.published.date(),
                'categories': result.categories,
                'pdf_url': result.pdf_url
            }
            papers.append(paper_data)
            logger.info(f"Fetched paper: {paper_data['title']}")

        return papers