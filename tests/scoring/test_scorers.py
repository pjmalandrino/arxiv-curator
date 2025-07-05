"""Tests for the scoring system."""

import pytest
import asyncio
from datetime import datetime, timedelta

from src.scoring import (
    Paper,
    KeywordScorer,
    TemporalScorer,
    CitationScorer,
    AuthorScorer,
    CompositeScorer,
    ScorerWeight,
    ScoringConfig,
    create_scorer,
    get_default_config
)


@pytest.fixture
def sample_paper():
    """Create a sample paper for testing."""
    return Paper(
        arxiv_id="2401.00001",
        title="Attention Is All You Need: A Revolutionary Transformer Architecture",
        abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms...",
        authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
        categories=["cs.CL", "cs.LG"],
        published_date=datetime.now() - timedelta(days=10),
        pdf_url="https://arxiv.org/pdf/2401.00001.pdf"
    )


@pytest.mark.asyncio
async def test_keyword_scorer(sample_paper):
    """Test keyword scoring functionality."""
    scorer = KeywordScorer(
        keywords=["transformer", "attention", "neural"],
        boost_terms={"revolutionary": 1.5, "simple": 0.8}
    )
    
    result = await scorer.score(sample_paper)
    
    assert 0 <= result.score <= 1.0
    assert "keyword_match" in result.components
    assert len(result.components) == 3
    assert "matched_keywords" in result.metadata


@pytest.mark.asyncio
async def test_temporal_scorer(sample_paper):
    """Test temporal scoring functionality."""
    scorer = TemporalScorer(
        trend_keywords={"transformer": 1.5, "attention": 1.2},
        peak_freshness_days=30
    )
    
    result = await scorer.score(sample_paper)
    
    assert 0 <= result.score <= 1.0
    assert "recency" in result.components
    assert "trending" in result.components
    assert "days_old" in result.metadata


@pytest.mark.asyncio
async def test_citation_scorer(sample_paper):
    """Test citation scoring functionality."""
    scorer = CitationScorer(min_citations=5)
    
    result = await scorer.score(sample_paper)
    
    assert 0 <= result.score <= 1.0
    assert "citation_density" in result.components
    assert "venue_impact" in result.components
    assert "estimated_citations" in result.metadata


@pytest.mark.asyncio
async def test_author_scorer(sample_paper):
    """Test author scoring functionality."""
    scorer = AuthorScorer(
        known_authors={"Vaswani": 0.9},
        institution_scores={"google": 0.9}
    )
    
    result = await scorer.score(sample_paper)
    
    assert 0 <= result.score <= 1.0
    assert "author_reputation" in result.components
    assert "team_composition" in result.components
    assert "team_size" in result.metadata


@pytest.mark.asyncio
async def test_composite_scorer(sample_paper):
    """Test composite scoring with multiple strategies."""
    keyword_scorer = KeywordScorer(keywords=["transformer"])
    temporal_scorer = TemporalScorer()
    
    composite = CompositeScorer([
        ScorerWeight(keyword_scorer, 0.6),
        ScorerWeight(temporal_scorer, 0.4)
    ])
    
    result = await composite.score(sample_paper)
    
    assert 0 <= result.score <= 1.0
    assert "keyword_scorer" in result.components
    assert "temporal_scorer" in result.components
    assert result.components["keyword_scorer"]["weight"] == 0.6


@pytest.mark.asyncio
async def test_config_based_scorer():
    """Test creating scorer from configuration."""
    config = ScoringConfig(
        use_llm=False,  # Skip LLM for tests
        llm_weight=0.0,
        keywords=["machine learning", "ai"],
        keyword_weight=0.5,
        citation_weight=0.3,
        temporal_weight=0.2,
        author_weight=0.0
    )
    
    scorer = create_scorer(config)
    assert isinstance(scorer, CompositeScorer)


def test_default_config():
    """Test default configuration is valid."""
    config = get_default_config()
    assert config.llm_weight + config.keyword_weight + config.citation_weight + \
           config.temporal_weight + config.author_weight == 1.0
    assert len(config.keywords) > 0
    assert len(config.trend_keywords) > 0
