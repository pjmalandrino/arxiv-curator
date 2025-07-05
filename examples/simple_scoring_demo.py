#!/usr/bin/env python3
"""
Simple demo of the scoring system without LLM dependency.
"""

import sys
sys.path.insert(0, '/Users/pjmalandrino/Documents/Pro/workspace/poc/arxiv-curator')

import asyncio
from datetime import datetime, timedelta
from src.scoring import (
    Paper,
    ScoringConfig,
    create_scorer,
    CompositeScorer,
    ScorerWeight,
    KeywordScorer,
    TemporalScorer,
    CitationScorer,
    AuthorScorer
)


async def demo_keyword_scoring():
    """Demo keyword-based scoring."""
    print("=== Keyword Scoring Demo ===\n")
    
    # Create a sample paper
    paper = Paper(
        arxiv_id="2401.12345",
        title="Attention Is All You Need: Transformer Architecture for NLP",
        abstract="We propose a new simple network architecture, the Transformer, based solely on "
                "attention mechanisms, dispensing with recurrence and convolutions entirely. "
                "This novel approach achieves state-of-the-art results on machine translation tasks.",
        authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
        categories=["cs.CL", "cs.LG"],
        published_date=datetime.now() - timedelta(days=5),
        pdf_url="https://arxiv.org/pdf/2401.12345.pdf"
    )
    
    # Create keyword scorer
    scorer = KeywordScorer(
        keywords=["transformer", "attention", "neural", "nlp"],
        boost_terms={"novel": 1.5, "state-of-the-art": 1.3}
    )
    
    result = await scorer.score(paper)
    print(f"Paper: {paper.title[:60]}...")
    print(f"Score: {result.score:.3f}")
    print(f"Explanation: {result.explanation}")
    print(f"Matched keywords: {result.metadata.get('matched_keywords', [])}")


async def demo_composite_scoring():
    """Demo composite scoring without LLM."""
    print("\n\n=== Composite Scoring Demo (No LLM) ===\n")
    
    # Recent AI safety paper
    paper = Paper(
        arxiv_id="2401.54321",
        title="Constitutional AI: Harmless and Helpful Language Models",
        abstract="We present Constitutional AI, a method for training harmless AI assistants "
                "without human feedback labels. Our approach uses a set of principles to guide "
                "the model's behavior. Published results show significant improvements in "
                "safety metrics while maintaining performance.",
        authors=["AI Safety Researcher", "Ethics Lab", "DeepMind"],
        categories=["cs.AI", "cs.CL"],
        published_date=datetime.now() - timedelta(days=2),
        pdf_url="https://arxiv.org/pdf/2401.54321.pdf"
    )
    
    # Create a composite scorer without LLM
    config = ScoringConfig(
        use_llm=False,
        llm_weight=0.0,
        keywords=["ai safety", "constitutional", "harmless", "ethical"],
        boost_terms={"safety": 1.5, "harmless": 1.3},
        keyword_weight=0.4,
        citation_weight=0.2,
        trend_keywords={"constitutional ai": 2.0, "ai safety": 1.5},
        temporal_weight=0.3,
        known_authors={"DeepMind": 0.9},
        author_weight=0.1
    )
    
    scorer = create_scorer(config)
    result = await scorer.score(paper)
    
    print(f"Paper: {paper.title}")
    print(f"Overall Score: {result.score:.3f}")
    print(f"\nComponent breakdown:")
    for component, data in result.components.items():
        if isinstance(data, dict):
            print(f"  {component}: {data.get('score', 0):.3f} (weight: {data.get('weight', 0):.2f})")


async def demo_individual_scorers():
    """Demo individual scoring components."""
    print("\n\n=== Individual Scorers Demo ===\n")
    
    # Create a test paper
    paper = Paper(
        arxiv_id="2401.99999",
        title="Efficient Training of Large Language Models at Scale",
        abstract="We introduce novel techniques for efficient training of large language models. "
                "Our method reduces computational requirements by 50% while maintaining performance. "
                "Experiments on GPT-scale models demonstrate significant improvements. "
                "Work done at Stanford University in collaboration with Google Research.",
        authors=["John Doe", "Jane Smith", "Stanford AI Lab"],
        categories=["cs.LG", "cs.CL"],
        published_date=datetime.now() - timedelta(days=7),
        pdf_url="https://arxiv.org/pdf/2401.99999.pdf"
    )
    
    # Test each scorer individually
    scorers = [
        ("Temporal", TemporalScorer(trend_keywords={"efficient": 1.5, "large language models": 1.8})),
        ("Citation", CitationScorer(min_citations=5)),
        ("Author", AuthorScorer(institution_scores={"stanford": 0.9, "google": 0.85}))
    ]
    
    for name, scorer in scorers:
        result = await scorer.score(paper)
        print(f"\n{name} Scorer:")
        print(f"  Score: {result.score:.3f}")
        print(f"  Explanation: {result.explanation}")


async def main():
    """Run all demos."""
    await demo_keyword_scoring()
    await demo_composite_scoring() 
    await demo_individual_scorers()
    
    print("\n\n✅ All demos completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
