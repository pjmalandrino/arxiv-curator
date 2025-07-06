"""Ollama client for local LLM scoring and analysis."""

import logging
import json
from typing import Dict, Any, Optional

import requests
from requests.exceptions import RequestException

from ..core.exceptions import SummarizationError
from ..core.config import OllamaConfig

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama local LLM API."""
    
    def __init__(self, config: OllamaConfig):
        """Initialize Ollama client.
        
        Args:
            config: Ollama configuration
        """
        self.config = config
        self.api_url = f"{config.host}/api/generate"
    
    def analyze_paper(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a paper using local LLM.
        
        Args:
            paper_data: Paper data dictionary
            
        Returns:
            Dict[str, Any]: Analysis results
            
        Raises:
            SummarizationError: If analysis fails
        """
        try:
            prompt = self._create_analysis_prompt(paper_data)
            
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise SummarizationError(error_msg)
            
            result = response.json()
            analysis_text = result.get("response", "")
            
            # Parse structured output if possible
            return self._parse_analysis(analysis_text)
            
        except RequestException as e:
            logger.error(f"Network error calling Ollama: {e}")
            raise SummarizationError(f"Ollama network error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in Ollama analysis: {e}")
            raise SummarizationError(f"Ollama analysis failed: {e}") from e
    
    def score_relevance(self, paper_data: Dict[str, Any]) -> float:
        """Score paper relevance using local LLM.
        
        Args:
            paper_data: Paper data dictionary
            
        Returns:
            float: Relevance score between 0 and 1
        """
        try:
            prompt = self._create_scoring_prompt(paper_data)
            
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent scoring
                    "max_tokens": 100
                }
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                logger.warning(f"Ollama scoring failed, using default score")
                return 0.5
            
            result = response.json()
            score_text = result.get("response", "")
            
            # Extract score from response
            score = self._extract_score(score_text)
            return score
            
        except Exception as e:
            logger.warning(f"Error scoring with Ollama: {e}, using default score")
            return 0.5
    
    def _create_analysis_prompt(self, paper_data: Dict[str, Any]) -> str:
        """Create analysis prompt for the LLM.
        
        Args:
            paper_data: Paper data dictionary
            
        Returns:
            str: Analysis prompt
        """
        return f"""Analyze the following research paper and provide insights:

Title: {paper_data.get('title', 'N/A')}
Authors: {', '.join(paper_data.get('authors', []))}
Abstract: {paper_data.get('abstract', 'N/A')}

Please provide:
1. Key innovations or contributions
2. Potential applications
3. Limitations or challenges
4. Relevance to current AI/ML trends

Format your response as JSON with keys: innovations, applications, limitations, relevance_notes"""

    def _create_scoring_prompt(self, paper_data: Dict[str, Any]) -> str:
        """Create scoring prompt for the LLM.
        
        Args:
            paper_data: Paper data dictionary
            
        Returns:
            str: Scoring prompt
        """
        return f"""Score the relevance of this AI/ML research paper from 0.0 to 1.0:

Title: {paper_data.get('title', 'N/A')}
Abstract: {paper_data.get('abstract', 'N/A')}

Consider:
- Relevance to LLMs, transformers, or language models
- Novelty and potential impact
- Technical contribution
- Practical applications

Respond with ONLY a number between 0.0 and 1.0"""

    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse analysis text to extract structured data.
        
        Args:
            analysis_text: Raw analysis text
            
        Returns:
            Dict[str, Any]: Parsed analysis
        """
        try:
            # Try to parse as JSON
            return json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback to text analysis
            return {
                "raw_analysis": analysis_text,
                "innovations": [],
                "applications": [],
                "limitations": [],
                "relevance_notes": analysis_text[:200]
            }

    def _extract_score(self, score_text: str) -> float:
        """Extract numerical score from text.
        
        Args:
            score_text: Text containing score
            
        Returns:
            float: Extracted score between 0 and 1
        """
        import re
        
        # Look for floating point number
        match = re.search(r'(\d*\.?\d+)', score_text.strip())
        if match:
            try:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))  # Clamp to [0, 1]
            except ValueError:
                pass
        
        # Default fallback
        return 0.5
