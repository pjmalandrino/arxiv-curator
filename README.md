# ArXiv Curator

An automated system that fetches, summarizes, and organizes AI research papers from ArXiv using HuggingFace's inference API.

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

3. **View papers**:
   Open http://localhost:5000

4. **Check logs**:
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

## Testing

```bash
docker-compose run --rm pipeline python -m pytest tests/
```
