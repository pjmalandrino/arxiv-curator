# Advanced Scoring System for arXiv Curator

## Overview

The scoring system provides a sophisticated multi-dimensional evaluation of arXiv papers based on various factors including content relevance, citation patterns, temporal trends, and author reputation.

## Components

### 1. **Composite Scorer**
Combines multiple scoring strategies with configurable weights to produce a final relevance score.

### 2. **Individual Scorers**

#### LLM Scorer
- Uses Ollama or other LLM providers to analyze paper content
- Evaluates novelty, technical quality, and potential impact
- Provides detailed explanations for scores

#### Keyword Scorer
- Matches against configured keywords and boost terms
- Uses TF-IDF-like scoring with partial matching
- Analyzes both title/abstract and categories

#### Citation Scorer
- Estimates citation density from abstract
- Identifies high-impact venue mentions
- Detects self-citation patterns
- Assesses reference quality

#### Temporal Scorer
- Rewards recent publications with configurable decay
- Identifies trending topics
- Includes publication timing optimization

#### Author Scorer
- Recognizes known researchers
- Evaluates team composition
- Detects multi-institutional collaboration
- Identifies prestigious institutions

## Configuration

### Basic Usage

```python
from scoring import get_default_config, create_scorer

# Use default configuration
config = get_default_config()
scorer = create_scorer(config)

# Score a paper
result = await scorer.score(paper)
print(f"Score: {result.score}")
print(f"Explanation: {result.explanation}")
```

### Custom Configuration

```python
from scoring import ScoringConfig, create_scorer

config = ScoringConfig(
    # LLM settings
    use_llm=True,
    llm_weight=0.3,
    
    # Keywords for your research area
    keywords=["quantum computing", "quantum algorithms"],
    boost_terms={"breakthrough": 1.5, "novel": 1.3},
    keyword_weight=0.3,
    
    # Citation analysis
    min_citations=10,
    citation_weight=0.2,
    
    # Trending topics
    trend_keywords={"quantum supremacy": 2.0, "NISQ": 1.5},
    temporal_weight=0.15,
    
    # Known researchers
    known_authors={"John Preskill": 0.9, "Peter Shor": 1.0},
    author_weight=0.05
)

scorer = create_scorer(config)
```

## Score Interpretation

- **0.0 - 0.3**: Low relevance - Paper has minimal alignment with configured interests
- **0.3 - 0.6**: Moderate relevance - Some interesting aspects but not highly aligned
- **0.6 - 0.8**: High relevance - Strong alignment with research interests
- **0.8 - 1.0**: Very high relevance - Exceptional match, likely important paper

## Integration with Pipeline

The scoring system is integrated into the main pipeline:

```python
# In main_v2.py
pipeline = ArxivCurationPipeline(config, scoring_config)
pipeline.run(days_back=7)
```

Papers below the configured threshold (`min_relevance_score`) are automatically filtered out.

## Advanced Features

### Fallback Mechanisms
- LLM scorer has fallback heuristics if API fails
- Non-required scorers won't break the pipeline

### Performance Optimization
- Asynchronous scoring for better performance
- Configurable rate limiting
- Batch processing support

### Extensibility
- Easy to add new scoring strategies
- Pluggable architecture
- Configuration-driven approach

## Database Integration

Scores are stored in the `paper_scores` table with:
- Individual component scores
- Detailed explanations
- Metadata for analysis
- Timestamp tracking

## Future Enhancements

1. **Machine Learning Integration**
   - Train custom models on user feedback
   - Learn personalized scoring weights

2. **External Data Sources**
   - Semantic Scholar API for citation counts
   - Author h-index integration
   - Conference acceptance rates

3. **Interactive Tuning**
   - Web interface for adjusting weights
   - Real-time score preview
   - A/B testing framework
