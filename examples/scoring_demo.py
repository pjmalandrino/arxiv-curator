#!/usr/bin/env python3
"""
Example usage of the advanced scoring system.

This script demonstrates how to use the scoring system standalone
without the full pipeline infrastructure.
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from datetime import datetime, timedelta
from src.scoring import (
    Paper,
    ScoringConfig,
    create_scorer,
    get_default_config,
    CompositeScorer,
    ScorerWeight,
    KeywordScorer,
    TemporalScorer
)


async def example_basic_scoring():
    """Basic example using default configuration."""
    print("=== Basic Scoring Example ===\n")
    
    # Create a sample paper
    paper = Paper(
        arxiv_id="2401.12345",
        title="Attention Mechanisms in Vision Transformers: A Comprehensive Survey",
        abstract="We present a comprehensive survey of attention mechanisms in vision transformers, "
                "focusing on recent advances in efficient attention computation. Our work introduces "
                "a novel taxonomy of attention patterns and demonstrates state-of-the-art results "
                "on ImageNet classification.",
        authors=["John Doe", "Jane Smith", "AI Lab"],
        categories=["cs.CV", "cs.LG"],
        published_date=datetime.now() - timedelta(days=5),
        pdf_url="https://arxiv.org/pdf/2401.12345.pdf"
    )
    
    # Use default scorer
    config = get_default_config()
    scorer = create_scorer(config)
    
    # Score the paper
    result = await scorer.score(paper)
    
    print(f"Paper: {paper.title}")
    print(f"Score: {result.score:.3f}")
    print(f"Explanation: {result.explanation}")
    print("\nComponent Scores:")
    for component, value in result.components.items():
        if isinstance(value, dict):
            print(f"  {component}: {value.get('score', 0):.3f}")
        else:
            print(f"  {component}: {value:.3f}")


async def example_custom_scoring():
    """Example with custom configuration for quantum computing papers."""
    print("\n\n=== Custom Scoring Example (Quantum Computing) ===\n")
    
    # Quantum computing paper
    paper = Paper(
        arxiv_id="2401.54321",
        title="Quantum Error Correction with Topological Codes: A Novel Approach",
        abstract="We introduce a breakthrough in quantum error correction using topological codes. "
                "Our novel approach achieves fault-tolerant quantum computation with significantly "
                "reduced overhead. Published in Nature Quantum Information.",
        authors=["Alice Quantum", "Bob Qubit", "MIT Quantum Lab"],
        categories=["quant-ph", "cs.IT"],
        published_date=datetime.now() - timedelta(days=15),
        pdf_url="https://arxiv.org/pdf/2401.54321.pdf"
    )
    
    # Custom config for quantum computing
    config = ScoringConfig(
        use_llm=False,  # Skip LLM for demo
        llm_weight=0.0,
        keywords=["quantum", "error correction", "topological", "fault-tolerant"],
        boost_terms={"breakthrough": 2.0, "novel": 1.5},
        keyword_weight=0.4,
        citation_weight=0.3,
        trend_keywords={"topological codes": 1.8, "quantum error correction": 1.5},
        temporal_weight=0.2,
        known_authors={"Alice Quantum": 0.9},
        institution_scores={"MIT": 0.95},
        author_weight=0.1
    )
    
    scorer = create_scorer(config)
    result = await scorer.score(paper)
    
    print(f"Paper: {paper.title}")
    print(f"Score: {result.score:.3f}")
    print(f"Explanation: {result.explanation}")


async def example_simple_scorer():
    """Example using individual scorers directly."""
    print("\n\n=== Simple Scorer Example ===\n")
    
    paper = Paper(
        arxiv_id="2401.99999",
        title="Efficient Training of Large Language Models",
        abstract="We present efficient methods for training large language models...",
        authors=["Researcher One"],
        categories=["cs.CL"],
        published_date=datetime.now() - timedelta(days=1),
        pdf_url="https://arxiv.org/pdf/2401.99999.pdf"
    )
    
    # Use just keyword and temporal scorers
    keyword_scorer = KeywordScorer(
        keywords=["efficient", "language model", "training"],
        boost_terms={"efficient": 1.5}
    )
    temporal_scorer = TemporalScorer(
        trend_keywords={"efficient": 1.3, "llm": 1.5}
    )
    
    # Create composite with just these two
    scorer = CompositeScorer([
        ScorerWeight(keyword_scorer, 0.7),
        ScorerWeight(temporal_scorer, 0.3)
    ])
    
    result = await scorer.score(paper)
    print(f"Paper: {paper.title}")
    print(f"Combined Score: {result.score:.3f}")
    print(f"Keyword component: {result.components['keyword_scorer']['score']:.3f}")
    print(f"Temporal component: {result.components['temporal_scorer']['score']:.3f}")


async def main():
    """Run all examples."""
    await example_basic_scoring()
    await example_custom_scoring()
    await example_simple_scorer()


if __name__ == "__main__":
    asyncio.run(main())
