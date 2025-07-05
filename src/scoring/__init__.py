"""Scoring module for arXiv paper relevance and quality assessment."""

from .base import ScoringStrategy, Paper, ScoringResult
from .composite_scorer import CompositeScorer, ScorerWeight
from .llm_scorer import LLMScorer
from .keyword_scorer import KeywordScorer
from .citation_scorer import CitationScorer
from .temporal_scorer import TemporalScorer
from .author_scorer import AuthorScorer
from .config import ScoringConfig, create_scorer, get_default_config

__all__ = [
    'ScoringStrategy',
    'Paper',
    'ScoringResult',
    'CompositeScorer',
    'ScorerWeight',
    'LLMScorer',
    'KeywordScorer',
    'CitationScorer',
    'TemporalScorer',
    'AuthorScorer',
    'ScoringConfig',
    'create_scorer',
    'get_default_config'
]
