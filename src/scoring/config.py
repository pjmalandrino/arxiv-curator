"""Scoring configuration and factory."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base import ScoringStrategy
from .composite_scorer import CompositeScorer, ScorerWeight
from .llm_scorer import LLMScorer
from .keyword_scorer import KeywordScorer
from .citation_scorer import CitationScorer
from .temporal_scorer import TemporalScorer
from .author_scorer import AuthorScorer


@dataclass
class ScoringConfig:
    """Configuration for the scoring system."""
    # LLM configuration
    use_llm: bool = True
    llm_weight: float = 0.3
    ollama_host: Optional[str] = None
    ollama_model: Optional[str] = None
    
    # Keyword configuration
    keywords: List[str] = None
    boost_terms: Dict[str, float] = None
    keyword_weight: float = 0.2
    
    # Citation configuration
    min_citations: int = 5
    citation_weight: float = 0.2
    
    # Temporal configuration
    trend_keywords: Dict[str, float] = None
    temporal_weight: float = 0.15
    peak_freshness_days: int = 30
    
    # Author configuration
    known_authors: Dict[str, float] = None
    institution_scores: Dict[str, float] = None
    author_weight: float = 0.15
    
    def __post_init__(self):
        """Validate configuration."""
        # Initialize empty collections if None
        if self.keywords is None:
            self.keywords = []
        if self.boost_terms is None:
            self.boost_terms = {}
        if self.trend_keywords is None:
            self.trend_keywords = {}
        if self.known_authors is None:
            self.known_authors = {}
        if self.institution_scores is None:
            self.institution_scores = {}
        
        # Validate weights sum to 1.0
        total_weight = (
            self.llm_weight + self.keyword_weight + self.citation_weight +
            self.temporal_weight + self.author_weight
        )
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Scorer weights must sum to 1.0, got {total_weight}")


def create_scorer(config: ScoringConfig) -> ScoringStrategy:
    """Create a composite scorer from configuration."""
    scorer_weights = []
    
    # Add LLM scorer
    if config.use_llm and config.llm_weight > 0:
        llm_scorer = LLMScorer(
            ollama_host=config.ollama_host,
            model=config.ollama_model
        )
        scorer_weights.append(
            ScorerWeight(llm_scorer, config.llm_weight, required=False)
        )
    
    # Add keyword scorer
    if config.keyword_weight > 0:
        keyword_scorer = KeywordScorer(
            keywords=config.keywords,
            boost_terms=config.boost_terms
        )
        scorer_weights.append(
            ScorerWeight(keyword_scorer, config.keyword_weight)
        )
    
    # Add citation scorer
    if config.citation_weight > 0:
        citation_scorer = CitationScorer(
            min_citations=config.min_citations
        )
        scorer_weights.append(
            ScorerWeight(citation_scorer, config.citation_weight)
        )
    
    # Add temporal scorer
    if config.temporal_weight > 0:
        temporal_scorer = TemporalScorer(
            trend_keywords=config.trend_keywords,
            peak_freshness_days=config.peak_freshness_days
        )
        scorer_weights.append(
            ScorerWeight(temporal_scorer, config.temporal_weight)
        )
    
    # Add author scorer
    if config.author_weight > 0:
        author_scorer = AuthorScorer(
            known_authors=config.known_authors,
            institution_scores=config.institution_scores
        )
        scorer_weights.append(
            ScorerWeight(author_scorer, config.author_weight)
        )
    
    # Normalize weights if needed
    if scorer_weights:
        total = sum(sw.weight for sw in scorer_weights)
        if abs(total - 1.0) > 0.001:
            # Normalize
            for sw in scorer_weights:
                sw.weight = sw.weight / total
    
    return CompositeScorer(scorer_weights)


def get_default_config() -> ScoringConfig:
    """Get a default scoring configuration with ML/AI focus."""
    return ScoringConfig(
        # LLM settings
        use_llm=True,
        llm_weight=0.3,
        
        # Keywords for ML/AI papers
        keywords=[
            "transformer", "attention", "neural", "deep learning",
            "reinforcement learning", "generative", "diffusion",
            "language model", "vision", "multimodal"
        ],
        boost_terms={
            "novel": 1.5,
            "state-of-the-art": 1.3,
            "breakthrough": 1.5,
            "efficient": 1.2,
            "scalable": 1.2
        },
        keyword_weight=0.2,
        
        # Citation settings
        min_citations=5,
        citation_weight=0.2,
        
        # Temporal settings
        trend_keywords={
            "llm": 1.5,
            "foundation model": 1.4,
            "mamba": 1.3,
            "diffusion": 1.2,
            "multimodal": 1.3,
            "efficient": 1.2
        },
        temporal_weight=0.15,
        peak_freshness_days=30,
        
        # Author settings
        known_authors={
            # Add prominent researchers in your field
            "Yann LeCun": 0.9,
            "Geoffrey Hinton": 0.9,
            "Yoshua Bengio": 0.9,
            "Ian Goodfellow": 0.85,
            "Andrej Karpathy": 0.85,
        },
        institution_scores={
            "mila": 0.9,
            "vector institute": 0.85,
            "fair": 0.9,
            "google brain": 0.9,
            "anthropic": 0.9
        },
        author_weight=0.15
    )
