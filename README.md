# ArXiv Curator

An intelligent system that fetches, scores, summarizes, and organizes AI research papers from ArXiv using advanced multi-dimensional scoring and HuggingFace's inference API.

## ✨ Key Features

- **Advanced Scoring System**: Multi-dimensional paper evaluation using:
  - LLM-based content analysis (via Ollama)
  - Keyword matching with boost terms
  - Citation pattern analysis
  - Temporal relevance and trending topics
  - Author reputation scoring
- **Automatic Filtering**: Only processes papers above relevance threshold
- **Paper Summarization**: Uses HuggingFace models for concise summaries
- **Web Interface**: Browse and search curated papers
- **Dockerized**: Easy deployment with Docker Compose

## Project Structure

```
arxiv-curator/
├── src/                    # Application source code
│   ├── main.py            # Pipeline entry point
│   ├── web_app.py         # Flask web interface
│   ├── arxiv_client.py    # ArXiv API client
│   ├── hf_client.py       # HuggingFace inference client
│   ├── database.py        # Database operations
│   ├── models.py          # SQLAlchemy models
│   └── config.py          # Configuration
├── templates/             # HTML templates
├── static/               # CSS and static files
├── database/             # Database schema
│   └── init/
│       └── 01_schema.sql
├── tests/                # Test files
│   └── test_integration.py
├── volumes/              # Docker volumes (gitignored)
├── .env                  # Environment variables
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # Single Dockerfile for all services
└── requirements.txt      # Python dependencies
```

## Quick Start

1. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your HuggingFace token
   ```
   
   Note: You'll need to:
   - Get a HuggingFace token from https://huggingface.co/settings/tokens
   - Set a secure PostgreSQL password
   - The default model is `facebook/bart-large-cnn`

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Run the enhanced pipeline** (with scoring):
   ```bash
   docker run --rm --network arxiv-curator-network \
     -e DATABASE_URL="postgresql://curator:YOUR_PASSWORD@postgres:5432/arxiv_curator" \
     -e HF_TOKEN="YOUR_HF_TOKEN" \
     -e OLLAMA_HOST="http://host.docker.internal:11434" \
     arxiv-curator-pipeline python -m src.main_v2
   ```

4. **View papers**:
   Open http://localhost:5000

5. **Check logs**:
   ```bash
   docker-compose logs -f pipeline
   ```

## Services

- **PostgreSQL**: Stores papers and summaries
- **Pipeline**: Fetches papers from ArXiv and generates summaries
- **Web**: Flask interface to browse curated papers

## Configuration

Edit `.env` to configure:
- `HF_TOKEN`: Your HuggingFace API token
- `HF_MODEL`: Model to use for summarization (default: facebook/bart-large-cnn)
- `POSTGRES_PASSWORD`: Database password
- `OLLAMA_HOST`: Ollama API endpoint (default: http://host.docker.internal:11434)
- `OLLAMA_MODEL`: Ollama model for scoring (default: gemma3:4b)

### Scoring Configuration

The scoring system can be customized in `src/main_v2.py`:

```python
scoring_config = ScoringConfig(
    # Keywords for your research area
    keywords=["machine learning", "neural networks", "transformer"],
    boost_terms={"novel": 1.5, "state-of-the-art": 1.3},
    
    # Component weights (must sum to 1.0)
    llm_weight=0.3,      # LLM content analysis
    keyword_weight=0.25,  # Keyword matching
    citation_weight=0.15, # Citation analysis
    temporal_weight=0.2,  # Recency and trends
    author_weight=0.1,    # Author reputation
    
    # Other settings
    min_citations=5,
    trend_keywords={"llm": 1.5, "rag": 1.4}
)
```

## Scoring System

The advanced scoring system evaluates papers across multiple dimensions:

1. **LLM Analysis** (via Ollama): Deep content understanding
2. **Keyword Matching**: Configurable terms with boost multipliers
3. **Citation Patterns**: Reference quality and venue analysis
4. **Temporal Factors**: Recency and trending topics
5. **Author Reputation**: Known researchers and institutions

Papers scoring below the threshold (default: 0.4) are automatically filtered out.

See `src/scoring/README.md` for detailed documentation.

## Testing

```bash
docker-compose run --rm pipeline python -m pytest tests/
```
