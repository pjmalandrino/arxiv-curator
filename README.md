# ArXiv Curator

A clean, modular Python application for automatically curating and summarizing research papers from ArXiv using AI/ML models.

## Features

- 🔍 **Automated Paper Discovery**: Fetches recent papers from ArXiv based on configured categories and keywords
- 🤖 **AI-Powered Summarization**: Uses HuggingFace models to generate concise summaries
- 📊 **Relevance Scoring**: Scores papers based on relevance to your research interests
- 🗄️ **PostgreSQL Storage**: Stores papers and summaries in a robust database
- 🌐 **Web Interface**: Clean Flask-based web UI for browsing papers
- 🔧 **Modular Architecture**: Clean, testable code following best practices

## Architecture

```
src/
├── core/               # Core business logic and configuration
│   ├── config.py      # Configuration management
│   └── exceptions.py  # Custom exceptions
├── domain/            # Domain models and entities
│   ├── entities.py    # Paper, Summary entities
│   └── value_objects.py # ArxivId, Score, etc.
├── infrastructure/    # External service integrations
│   ├── database.py    # Database management
│   ├── arxiv.py       # ArXiv API client
│   ├── huggingface.py # HuggingFace client
│   └── ollama.py      # Ollama client (optional)
├── services/          # Application services
│   ├── curation_service.py # Paper processing logic
│   └── pipeline_service.py # Pipeline orchestration
├── web/              # Web application
│   ├── app.py        # Flask app factory
│   └── routes.py     # API routes
└── utils/            # Utility functions
    ├── logging.py    # Logging setup
    └── validators.py # Input validation
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- HuggingFace API token (get one at https://huggingface.co/settings/tokens)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd arxiv-curator
```

2. Copy the example environment file and configure:
```bash
cp .env.example .env
# Edit .env and add your HF_TOKEN
```

3. Start the services:
```bash
docker-compose up -d
```

The application will:
- Create a PostgreSQL database
- Run the curation pipeline to fetch and process papers
- Start a web interface at http://localhost:5000

### Using the Application

#### Running the Pipeline Manually

```bash
docker-compose run --rm pipeline python -m src.main
```

#### Accessing the Web Interface

Open http://localhost:5000 in your browser to:
- View recently curated papers
- Read AI-generated summaries
- Filter by relevance score

#### API Endpoints

- `GET /api/papers` - List recent papers
  - Query params: `days`, `limit`, `min_score`
- `GET /api/paper/<arxiv_id>` - Get specific paper
- `GET /api/stats` - Get curation statistics

## Configuration

### Environment Variables

See `.env.example` for all available configuration options. Key settings:

- **Database**: Configure PostgreSQL connection
- **HuggingFace**: API token and model selection
- **ArXiv**: Categories, keywords, and search parameters
- **Processing**: Batch size, retry logic, scoring thresholds

### Customizing Paper Categories

Edit `ARXIV_CATEGORIES` in your `.env` file:
```
ARXIV_CATEGORIES=cs.CL,cs.AI,cs.LG,stat.ML
```

### Adding Keywords

Modify `ARXIV_KEYWORDS` to focus on specific topics:
```
ARXIV_KEYWORDS=reinforcement learning,neural architecture search,vision transformer
```

## Development

### Code Quality

The project follows clean code principles:
- Type hints throughout
- Comprehensive error handling
- Dependency injection
- SOLID principles
- Domain-driven design

### Running Tests

```bash
docker-compose -f docker-compose.test.yml run --rm tests
```

### Code Formatting

```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing patterns
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details
