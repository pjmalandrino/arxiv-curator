"""Paper curation service for processing individual papers."""

import logging
from typing import Optional, Dict, Any
from uuid import uuid4

from ..core.exceptions import ArxivCuratorError, SummarizationError
from ..domain.entities import Paper, Summary, SummaryResult
from ..infrastructure import (
    DatabaseManager,
    ArxivClient,
    HuggingFaceClient,
    OllamaClient
)

logger = logging.getLogger(__name__)


class CurationService:
    """Service for curating research papers."""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        arxiv_client: ArxivClient,
        hf_client: HuggingFaceClient,
        ollama_client: Optional[OllamaClient] = None
    ):
        """Initialize curation service.
        
        Args:
            db_manager: Database manager
            arxiv_client: ArXiv API client
            hf_client: HuggingFace API client
            ollama_client: Optional Ollama client for local scoring
        """
        self.db_manager = db_manager
        self.arxiv_client = arxiv_client
        self.hf_client = hf_client
        self.ollama_client = ollama_client

    def process_paper(self, paper_data: Dict[str, Any]) -> Optional[Paper]:
        """Process a single paper through the curation pipeline.
        
        Args:
            paper_data: Paper data from ArXiv
            
        Returns:
            Optional[Paper]: Processed paper or None if skipped
        """
        try:
            # Check if paper already exists
            if self.db_manager.paper_exists(paper_data["arxiv_id"]):
                logger.info(f"Paper {paper_data['arxiv_id']} already exists")
                return None
            
            # Create paper entity
            paper = Paper.from_arxiv_data(paper_data)
            
            # Save paper to database
            saved_paper = self.db_manager.save_paper(paper)
            
            # Generate summary
            summary_result = self._generate_summary(paper_data)
            
            if summary_result:
                # Create and save summary
                summary = Summary(
                    paper_id=saved_paper.id,
                    result=summary_result
                )
                self.db_manager.save_summary(summary)
                
                logger.info(
                    f"Successfully processed paper: {paper.metadata.arxiv_id} "
                    f"(score: {summary_result.relevance_score:.2f})"
                )
            
            return saved_paper
            
        except Exception as e:
            logger.error(f"Error processing paper {paper_data.get('arxiv_id')}: {e}")
            raise ArxivCuratorError(f"Paper processing failed: {e}") from e

    def _generate_summary(self, paper_data: Dict[str, Any]) -> Optional[SummaryResult]:
        """Generate summary for a paper.
        
        Args:
            paper_data: Paper data
            
        Returns:
            Optional[SummaryResult]: Summary result or None if failed
        """
        try:
            # Generate summary using HuggingFace
            summary_result = self.hf_client.summarize_paper(paper_data)
            
            # Enhance with local LLM scoring if available
            if self.ollama_client:
                try:
                    enhanced_score = self.ollama_client.score_relevance(paper_data)
                    # Average the scores
                    summary_result.relevance_score = (
                        summary_result.relevance_score + enhanced_score
                    ) / 2
                except Exception as e:
                    logger.warning(f"Ollama scoring failed, using HF score only: {e}")
            
            return summary_result
            
        except SummarizationError as e:
            logger.error(f"Summarization failed: {e}")
            return None
    
    def rescore_paper(self, arxiv_id: str) -> Optional[float]:
        """Rescore an existing paper.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            Optional[float]: New relevance score or None if failed
        """
        if not self.ollama_client:
            logger.warning("Ollama client not available for rescoring")
            return None
        
        try:
            # Fetch paper data
            paper_data = self.arxiv_client.fetch_paper_by_id(arxiv_id)
            
            # Score with Ollama
            new_score = self.ollama_client.score_relevance(paper_data)
            
            logger.info(f"Rescored paper {arxiv_id}: {new_score:.2f}")
            return new_score
            
        except Exception as e:
            logger.error(f"Failed to rescore paper {arxiv_id}: {e}")
            return None
