"""Example integration of the scoring system with the arXiv curator."""

import asyncio
from datetime import datetime
from typing import Dict, Any, List

from .scoring import (
    ScoringConfig,
    create_scorer,
    get_default_config,
    Paper,
    CompositeScorer,
    ScorerWeight,
    LLMScorer,
    KeywordScorer
)


async def score_arxiv_paper(arxiv_data: Dict[str, Any], config: ScoringConfig = None) -> Dict[str, Any]:
    """
    Score an arXiv paper using the configured scoring system.
    
    Args:
        arxiv_data: Dictionary with arxiv paper data
        config: Scoring configuration (uses default if None)
    
    Returns:
        Dictionary with score results and metadata
    """
    # Use default config if none provided
    if config is None:
        config = get_default_config()
    
    # Create scorer
    scorer = create_scorer(config)
    
    # Convert arxiv data to Paper object
    paper = Paper(
        arxiv_id=arxiv_data['id'],
        title=arxiv_data['title'],
        abstract=arxiv_data['summary'],
        authors=[author['name'] for author in arxiv_data.get('authors', [])],
        categories=arxiv_data.get('categories', []),
        published_date=arxiv_data.get('published', datetime.now()),
        pdf_url=arxiv_data.get('pdf_url', ''),
        metadata=arxiv_data
    )
    
    # Create context from user preferences (if available)
    context = {
        'research_interests': config.keywords,
        'keywords': config.keywords
    }
    
    # Score the paper
    result = await scorer.score(paper, context)
    
    return {
        'arxiv_id': paper.arxiv_id,
        'title': paper.title,
        'score': result.score,
        'explanation': result.explanation,
        'component_scores': result.components,
        'metadata': result.metadata,
        'timestamp': datetime.now().isoformat()
    }


async def batch_score_papers(papers: List[Dict[str, Any]], config: ScoringConfig = None) -> List[Dict[str, Any]]:
    """Score multiple papers concurrently."""
    tasks = [score_arxiv_paper(paper, config) for paper in papers]
    return await asyncio.gather(*tasks)


def create_custom_scorer_example():
    """Example of creating a custom scorer with specific requirements."""
    # Example 1: Simple keyword-focused scorer
    simple_config = ScoringConfig(
        use_llm=False,  # No LLM for speed
        llm_weight=0.0,
        keywords=["quantum computing", "quantum algorithms", "qubit"],
        keyword_weight=0.6,
        citation_weight=0.2,
        temporal_weight=0.2,
        author_weight=0.0
    )
    
    # Example 2: Author-focused scorer for following specific researchers
    author_config = ScoringConfig(
        use_llm=True,
        llm_weight=0.2,
        known_authors={
            "John Doe": 1.0,
            "Jane Smith": 0.9,
            "Research Team": 0.8
        },
        author_weight=0.5,
        keyword_weight=0.1,
        citation_weight=0.1,
        temporal_weight=0.1
    )
    
    return simple_config, author_config


# Example usage for direct scoring without the full pipeline
async def example_direct_scoring():
    """Example of using the scoring system directly."""
    # Create a custom scorer focusing on trending topics
    config = ScoringConfig(
        use_llm=True,
        llm_weight=0.4,
        keywords=["ai safety", "alignment", "interpretability"],
        keyword_weight=0.3,
        trend_keywords={
            "constitutional ai": 2.0,
            "rlhf": 1.5,
            "chain of thought": 1.5,
            "emergent": 1.3
        },
        temporal_weight=0.3,
        citation_weight=0.0,  # Disable citation scoring
        author_weight=0.0     # Disable author scoring
    )
    
    # Create the scorer
    scorer = create_scorer(config)
    
    # Example paper data
    paper = Paper(
        arxiv_id="2401.12345",
        title="Constitutional AI: A Novel Approach to AI Safety Through RLHF",
        abstract="We present a new method for training AI systems to be helpful, harmless, and honest...",
        authors=["AI Researcher"],
        categories=["cs.AI", "cs.LG"],
        published_date=datetime.now(),
        pdf_url="https://arxiv.org/pdf/2401.12345.pdf"
    )
    
    # Score the paper
    result = await scorer.score(paper)
    print(f"Score: {result.score:.2f}")
    print(f"Explanation: {result.explanation}")
    print(f"Components: {result.components}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_direct_scoring())
