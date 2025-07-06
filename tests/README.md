# Testing Guide for arXiv Curator

## Overview

This document provides comprehensive guidance on testing the arXiv Curator application. Our testing strategy ensures reliability, performance, and maintainability of the codebase.

## Test Structure

```
tests/
├── conftest.py           # Global fixtures and configuration
├── fixtures/             # Test data and factories
│   ├── test_data.py     # Static test data
│   └── factories.py     # Data factories
├── unit/                # Unit tests
│   ├── test_models.py
│   ├── test_database.py
│   ├── test_arxiv_client.py
│   ├── test_hf_client.py
│   └── scoring/
│       ├── test_keyword_scorer.py
│       └── test_temporal_scorer.py
├── integration/         # Integration tests
│   ├── test_pipeline.py
│   ├── test_db_operations.py
│   └── test_scoring_system.py
├── e2e/                # End-to-end tests
│   ├── test_web_interface.py
│   └── test_docker_setup.py
├── performance/        # Performance tests
│   ├── test_batch_processing.py
│   └── test_memory_usage.py
└── utils.py           # Test utilities
```

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```
### Using Make Commands

```bash
# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run all tests with coverage
make test-all

# Run tests in Docker
make test-docker

# Clean test artifacts
make clean-test
```

### Test Categories

#### Unit Tests
Fast, isolated tests for individual components:
```bash
pytest tests/unit -v
```

#### Integration Tests
Tests for component interactions:
```bash
pytest tests/integration -v
```

#### End-to-End Tests
Full workflow tests including web interface:
```bash
pytest tests/e2e -v -m e2e
```

#### Performance Tests
Tests for performance and scalability:
```bash
pytest tests/performance -v -m performance
```

## Writing Tests

### Test Fixtures

Use provided fixtures for common test data:
```python
def test_paper_creation(sample_paper_data):
    """sample_paper_data fixture provides test paper data"""
    paper = Paper(**sample_paper_data)
    assert paper.arxiv_id == '2401.12345'
```

### Mocking External Services

```python
def test_with_mock_arxiv(mock_arxiv_client):
    """mock_arxiv_client provides pre-configured mock"""
    papers = mock_arxiv_client.fetch_recent_papers()
    assert len(papers) > 0
```

### Database Testing

```python
def test_database_operation(db_manager):
    """db_manager provides test database connection"""
    paper = db_manager.save_paper(test_data)
    assert paper.id is not None
```

## Test Data

### Using Factories

```python
from tests.fixtures.factories import PaperFactory, LLMPaperFactory

# Generate random paper
paper = PaperFactory()

# Generate LLM-specific paper
llm_paper = LLMPaperFactory()
```

### Static Test Data

```python
from tests.fixtures.test_data import TEST_PAPERS, TEST_SUMMARIES

# Use predefined test papers
paper_data = TEST_PAPERS[0]
```
## Coverage Requirements

- Unit tests: 80%+ coverage
- Integration tests: All critical paths
- E2E tests: Main user journeys

View coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## CI/CD Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Manual trigger

GitHub Actions workflow includes:
- PostgreSQL service container
- Unit and integration tests
- Coverage reporting
- Test result artifacts

## Debugging Tests

### Run specific test
```bash
pytest tests/unit/test_models.py::TestPaperModel::test_paper_creation -v
```

### Enable debugging output
```bash
pytest -v -s --log-cli-level=DEBUG
```

### Use debugger
```python
import pdb; pdb.set_trace()
```

## Performance Testing

Monitor test performance:
```bash
pytest tests/performance --durations=10
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Speed**: Unit tests should be fast (<100ms)
4. **Reliability**: Tests should not be flaky
5. **Coverage**: Aim for high coverage but focus on quality

## Troubleshooting

### Database Issues
- Ensure PostgreSQL is running for integration tests
- Check DATABASE_URL environment variable
- Use `--no-cov` flag if coverage causes issues

### Mock Issues
- Verify mock return values match expected format
- Use `spec=` parameter for strict mocking
- Check mock call counts with `assert_called_once()`

### Docker Tests
- Ensure Docker daemon is running
- Check container logs: `docker logs arxiv_test_runner`
- Verify network connectivity between containers