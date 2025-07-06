# ArXiv Curator Testing Makefile

.PHONY: test test-unit test-integration test-e2e test-performance test-all
.PHONY: test-docker test-coverage clean-test install-test-deps

# Install test dependencies
install-test-deps:
	pip install -r requirements-test.txt

# Run all tests
test: test-unit test-integration

# Run unit tests only
test-unit:
	pytest tests/unit -v -m "not slow"

# Run integration tests
test-integration:
	pytest tests/integration -v

# Run end-to-end tests
test-e2e:
	pytest tests/e2e -v -m "e2e"

# Run performance tests
test-performance:
	pytest tests/performance -v -m "performance"

# Run all tests with coverage
test-all:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Run tests in Docker
test-docker:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml down

# Run specific test file
test-file:
	@read -p "Enter test file path: " filepath; \
	pytest $$filepath -v

# Run tests with coverage report
test-coverage:
	pytest tests/ --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"
	@python -m webbrowser htmlcov/index.html

# Clean test artifacts
clean-test:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run tests in watch mode (requires pytest-watch)
test-watch:
	ptw tests/ --runner "pytest -v"

# Run tests with different markers
test-fast:
	pytest -v -m "not slow and not docker"

test-slow:
	pytest -v -m "slow"

# Lint tests
lint-tests:
	flake8 tests/ --max-line-length=100
	pylint tests/

# Type check tests
type-check-tests:
	mypy tests/ --ignore-missing-imports