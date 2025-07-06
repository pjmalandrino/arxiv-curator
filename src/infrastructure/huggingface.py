"""HuggingFace API client for paper summarization."""

import logging
from typing import Dict, Any, List
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..core.exceptions import SummarizationError
from ..core.config import HuggingFaceConfig
from ..domain.entities import SummaryResult

logger = logging.getLogger(__name__)


class HuggingFaceClient:
    """Client for HuggingFace API summarization."""
    
    API_URL = "https://api-inference.huggingface.co/models/{model}"
    
    def __init__(self, config: HuggingFaceConfig):
        """Initialize HuggingFace client.
        
        Args:
            config: HuggingFace configuration
        """
        self.config = config
        self.headers = {"Authorization": f"Bearer {config.api_key}"}
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

    def summarize_paper(self, paper_data: Dict[str, Any]) -> SummaryResult:
        """Summarize a research paper.
        
        Args:
            paper_data: Paper data dictionary
            
        Returns:
            SummaryResult: Summary result with key points and score
            
        Raises:
            SummarizationError: If summarization fails
        """
        try:
            # Prepare text for summarization
            text = self._prepare_text(paper_data)
            
            # Call HuggingFace API
            api_url = self.API_URL.format(model=self.config.model)
            payload = {
                "inputs": text,
                "parameters": {
                    "max_length": self.config.max_length,
                    "min_length": self.config.min_length,
                    "do_sample": False
                }
            }
            
            response = self.session.post(
                api_url,
                headers=self.headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise SummarizationError(error_msg)

            # Parse response
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                summary_text = result[0].get("summary_text", "")
            elif isinstance(result, dict):
                summary_text = result.get("summary_text", "")
            else:
                summary_text = str(result)
            
            if not summary_text:
                raise SummarizationError("Empty summary returned from API")
            
            # Extract key points
            key_points = self._extract_key_points(summary_text)
            
            # Calculate relevance score (placeholder - can be enhanced)
            relevance_score = self._calculate_relevance_score(paper_data, summary_text)
            
            return SummaryResult(
                summary=summary_text,
                key_points=key_points,
                relevance_score=relevance_score,
                model_used=self.config.model
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during summarization: {e}")
            raise SummarizationError(f"Network error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during summarization: {e}")
            raise SummarizationError(f"Summarization failed: {e}") from e

    def _prepare_text(self, paper_data: Dict[str, Any]) -> str:
        """Prepare paper text for summarization.
        
        Args:
            paper_data: Paper data dictionary
            
        Returns:
            str: Prepared text
        """
        title = paper_data.get("title", "")
        abstract = paper_data.get("abstract", "")
        
        # Combine title and abstract
        text = f"Title: {title}\n\nAbstract: {abstract}"
        
        # Truncate if too long
        max_chars = 5000  # Reasonable limit for most models
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """Extract key points from summary.
        
        Args:
            summary: Summary text
            
        Returns:
            List[str]: Key points
        """
        # Simple extraction - split by sentences
        sentences = summary.split(". ")
        
        # Take first 3-5 sentences as key points
        key_points = []
        for i, sentence in enumerate(sentences[:5]):
            if len(sentence.strip()) > 20:  # Filter out very short sentences
                key_points.append(sentence.strip() + ".")
        
        return key_points

    def _calculate_relevance_score(self, paper_data: Dict[str, Any], summary: str) -> float:
        """Calculate relevance score for a paper.
        
        Args:
            paper_data: Paper data dictionary
            summary: Generated summary
            
        Returns:
            float: Relevance score between 0 and 1
        """
        # Simple scoring based on keyword presence
        score = 0.5  # Base score
        
        keywords = ["llm", "language model", "transformer", "gpt", "bert", 
                   "neural", "deep learning", "attention", "pretrain", "finetune"]
        
        # Check title and abstract
        text = (paper_data.get("title", "") + " " + 
                paper_data.get("abstract", "") + " " + 
                summary).lower()
        
        # Count keyword occurrences
        keyword_count = sum(1 for keyword in keywords if keyword in text)
        
        # Adjust score based on keyword density
        score += min(keyword_count * 0.05, 0.5)
        
        return min(score, 1.0)
