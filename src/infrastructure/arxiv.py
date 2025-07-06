"""ArXiv API client for fetching research papers."""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

import arxiv

from ..core.exceptions import ArxivClientError
from ..core.config import ArxivConfig

logger = logging.getLogger(__name__)


class ArxivClient:
    """Client for interacting with the ArXiv API."""
    
    def __init__(self, config: ArxivConfig):
        """Initialize ArXiv client.
        
        Args:
            config: ArXiv configuration
        """
        self.config = config
        self.client = arxiv.Client()
    
    def fetch_recent_papers(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Fetch recent papers from ArXiv.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: List of paper data dictionaries
            
        Raises:
            ArxivClientError: If fetching fails
        """
        try:
            # Build search query
            query_parts = []
            
            # Add category filters
            if self.config.categories:
                cat_query = " OR ".join([f"cat:{cat}" for cat in self.config.categories])
                query_parts.append(f"({cat_query})")
            
            # Add keyword filters
            if self.config.keywords:
                keyword_query = " OR ".join([f'all:"{kw}"' for kw in self.config.keywords])
                query_parts.append(f"({keyword_query})")

            # Combine queries
            query = " AND ".join(query_parts) if query_parts else "all:*"
            
            logger.info(f"Searching ArXiv with query: {query}")
            
            # Create search
            search = arxiv.Search(
                query=query,
                max_results=self.config.max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            # Fetch results with rate limiting
            papers = []
            for result in self.client.results(search):
                paper_data = self._parse_paper(result)
                
                # Filter by date
                if days_back:
                    cutoff_date = datetime.now() - timedelta(days=days_back)
                    if paper_data["published_date"] < cutoff_date.date():
                        continue
                
                papers.append(paper_data)
                
                # Rate limiting
                time.sleep(self.config.rate_limit_delay)
            
            logger.info(f"Fetched {len(papers)} papers from ArXiv")
            return papers
            
        except Exception as e:
            logger.error(f"Failed to fetch papers from ArXiv: {e}")
            raise ArxivClientError(f"Failed to fetch papers: {e}") from e

    def _parse_paper(self, result: arxiv.Result) -> Dict[str, Any]:
        """Parse ArXiv result into paper data.
        
        Args:
            result: ArXiv search result
            
        Returns:
            Dict[str, Any]: Parsed paper data
        """
        return {
            "arxiv_id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "published_date": result.published.date(),
            "categories": result.categories,
            "pdf_url": result.pdf_url
        }
    
    def fetch_paper_by_id(self, arxiv_id: str) -> Dict[str, Any]:
        """Fetch a specific paper by ArXiv ID.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            Dict[str, Any]: Paper data
            
        Raises:
            ArxivClientError: If paper not found or fetch fails
        """
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            results = list(self.client.results(search))
            
            if not results:
                raise ArxivClientError(f"Paper not found: {arxiv_id}")
            
            return self._parse_paper(results[0])
            
        except Exception as e:
            logger.error(f"Failed to fetch paper {arxiv_id}: {e}")
            raise ArxivClientError(f"Failed to fetch paper: {e}") from e
