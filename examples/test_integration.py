#!/usr/bin/env python3
"""
Test the scoring system integration with mock data.
"""

import sys
sys.path.insert(0, '/Users/pjmalandrino/Documents/Pro/workspace/poc/arxiv-curator')

import asyncio
from datetime import datetime, timedelta
from src.scoring import (
    ScoringConfig,
    create_scorer,
    get_default_config,
    Paper
)
from src.scoring_integration import score_arxiv_paper, batch_score_papers


async def test_scoring_integration():
    """Test the scoring integration with mock arXiv data."""
    print("=== Testing Scoring Integration ===\n")
    
    # Mock arXiv paper data (similar to what arxiv_client would return)
    arxiv_papers = [
        {
            'id': '2401.00001',
            'arxiv_id': '2401.00001',
            'title': 'Scaling Laws for Neural Language Models',
            'summary': 'We study empirical scaling laws for language model performance on the '
                      'cross-entropy loss. The loss scales as a power-law with model size, '
                      'dataset size, and the amount of compute used for training. This has '
                      'implications for efficient training of large language models.',
            'authors': [{'name': 'AI Researcher'}],
            'categories': ['cs.LG', 'cs.CL'],
            'published': datetime.now() - timedelta(days=3),
            'pdf_url': 'https://arxiv.org/pdf/2401.00001.pdf'
        },
        {
            'id': '2401.00002', 
            'arxiv_id': '2401.00002',
            'title': 'Quantum Machine Learning: A Survey',
            'summary': 'This paper provides a comprehensive survey of quantum machine learning, '
                      'covering quantum algorithms for supervised and unsupervised learning.',
            'authors': [{'name': 'Quantum Researcher'}],
            'categories': ['quant-ph', 'cs.LG'],
            'published': datetime.now() - timedelta(days=10),
            'pdf_url': 'https://arxiv.org/pdf/2401.00002.pdf'
        },
        {
            'id': '2401.00003',
            'arxiv_id': '2401.00003', 
            'title': 'Efficient Attention Mechanisms for Transformers',
            'summary': 'We propose FlashAttention, a novel attention algorithm that reduces '
                      'memory usage and increases throughput of Transformer models. Our method '
                      'achieves state-of-the-art efficiency on long sequences.',
            'authors': [{'name': 'ML Engineer'}, {'name': 'Research Scientist'}],
            'categories': ['cs.LG', 'cs.CL'],
            'published': datetime.now() - timedelta(days=1),
            'pdf_url': 'https://arxiv.org/pdf/2401.00003.pdf'
        }
    ]
    
    # Test individual scoring
    print("Testing individual paper scoring:")
    config = get_default_config()
    config.use_llm = False  # Disable LLM for testing
    config.llm_weight = 0.0
    
    for paper in arxiv_papers:
        result = await score_arxiv_paper(paper, config)
        print(f"\n📄 {result['title'][:60]}...")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Explanation: {result['explanation'][:100]}...")
    
    # Test batch scoring
    print("\n\nTesting batch scoring:")
    results = await batch_score_papers(arxiv_papers, config)
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n📊 Ranking by relevance score:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title'][:50]}... - Score: {result['score']:.3f}")


async def test_custom_config():
    """Test with custom configuration."""
    print("\n\n=== Testing with Custom Configuration ===\n")
    
    # Custom config for quantum computing focus
    quantum_config = ScoringConfig(
        use_llm=False,
        llm_weight=0.0,
        keywords=["quantum", "qubit", "quantum computing", "quantum algorithms"],
        boost_terms={"breakthrough": 1.5, "novel": 1.3},
        keyword_weight=0.5,
        citation_weight=0.2,
        trend_keywords={"quantum": 1.5},
        temporal_weight=0.2,
        author_weight=0.1
    )
    
    # Test papers
    papers = [
        {
            'id': 'quantum-1',
            'arxiv_id': 'quantum-1',
            'title': 'Novel Quantum Algorithm for Integer Factorization',
            'summary': 'We present a breakthrough quantum algorithm that improves upon Shor\'s algorithm...',
            'authors': [{'name': 'Quantum Expert'}],
            'categories': ['quant-ph'],
            'published': datetime.now() - timedelta(days=2),
            'pdf_url': 'https://arxiv.org/pdf/quantum-1.pdf'
        },
        {
            'id': 'ml-1',
            'arxiv_id': 'ml-1',
            'title': 'Deep Learning for Image Recognition',
            'summary': 'A standard deep learning approach for image classification...',
            'authors': [{'name': 'ML Researcher'}],
            'categories': ['cs.CV'],
            'published': datetime.now() - timedelta(days=5),
            'pdf_url': 'https://arxiv.org/pdf/ml-1.pdf'
        }
    ]
    
    print("Scoring with quantum-focused configuration:")
    for paper in papers:
        result = await score_arxiv_paper(paper, quantum_config)
        print(f"\n📄 {result['title']}")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Components: {result['component_scores']}")


async def main():
    """Run all tests."""
    await test_scoring_integration()
    await test_custom_config()
    print("\n\n✅ All integration tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
