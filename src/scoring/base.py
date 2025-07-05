"""Base classes and interfaces for scoring strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class Paper:
    """Paper data structure for scoring."""
    arxiv_id: str
    title: str
    abstract: str
    authors: List[str]
    categories: List[str]
    published_date: datetime
    pdf_url: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ScoringResult:
    """Result from a scoring operation."""
    score: float  # 0.0 to 1.0
    explanation: str
    components: Dict[str, float]  # Individual component scores
    metadata: Dict[str, Any]  # Additional scoring metadata


class ScoringStrategy(ABC):
    """Abstract base class for scoring strategies."""
    
    @abstractmethod
    async def score(self, paper: Paper, context: Optional[Dict[str, Any]] = None) -> ScoringResult:
        """
        Score a paper based on the implementation strategy.
        
        Args:
            paper: Paper object to score
            context: Optional context for scoring (e.g., user preferences, research focus)
            
        Returns:
            ScoringResult with score and explanation
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this scoring strategy."""
        pass
