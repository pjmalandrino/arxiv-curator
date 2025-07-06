.PHONY: help build up down logs shell test format lint clean

# Default target
help:
	@echo "ArXiv Curator - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build       Build Docker images"
	@echo "  up          Start all services"
	@echo "  down        Stop all services"
	@echo "  logs        View logs"
	@echo "  shell       Open shell in pipeline container"
	@echo "  test        Run tests"
	@echo "  format      Format code with black"
	@echo "  lint        Run linting checks"
	@echo "  clean       Clean up containers and volumes"
	@echo "  run         Run the pipeline once"
	@echo "  web         Access web interface"

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d
	@echo "Services started. Web interface at http://localhost:5000"

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Open shell
shell:
	docker-compose run --rm pipeline bash

# Run tests
test:
	docker-compose -f docker-compose.test.yml run --rm tests

# Format code
format:
	@echo "Formatting code with black..."
	@docker run --rm -v $$(pwd):/app -w /app python:3.11-slim sh -c "pip install black && black src/"

# Lint code
lint:
	@echo "Running linting checks..."
	@docker run --rm -v $$(pwd):/app -w /app python:3.11-slim sh -c "pip install flake8 mypy && flake8 src/ && mypy src/"

# Clean up
clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run pipeline once
run:
	docker-compose run --rm pipeline python -m src.main

# Open web interface
web:
	@echo "Opening web interface..."
	@open http://localhost:5000 || xdg-open http://localhost:5000 || echo "Please open http://localhost:5000 in your browser"
