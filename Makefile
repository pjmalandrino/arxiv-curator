.PHONY: help build up down logs test clean pipeline view test-ollama fetch-new reset-db shell

help:
	@echo "ArXiv Curator - Available Commands:"
	@echo ""
	@echo "Core Commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs (Ctrl+C to exit)"
	@echo "  make pipeline   - Run the pipeline to fetch papers"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make view       - View papers in database"
	@echo "  make test-ollama - Test Ollama connection"
	@echo "  make fetch-new  - Fetch new papers with custom search"
	@echo "  make reset-db   - Clear database (WARNING: deletes all data)"
	@echo "  make clean      - Clean up everything including volumes"
	@echo "  make shell      - Open shell in pipeline container"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

pipeline:
	docker-compose run --rm pipeline python scripts/run_pipeline.py

view:
	@echo "📊 Viewing papers in database..."
	@docker-compose run --rm pipeline python scripts/view_papers.py

test-ollama:
	@echo "🧪 Testing Ollama connection..."
	@docker-compose run --rm pipeline python scripts/test_ollama.py

fetch-new:
	@echo "🔍 Fetching new papers..."
	@docker-compose run --rm pipeline python scripts/fetch_new_papers.py $(ARGS)

reset-db:
	@echo "⚠️  WARNING: This will delete all papers and summaries!"
	@read -p "Are you sure? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "Resetting database..."
	@docker-compose down -v
	@docker-compose up -d postgres
	@sleep 5
	@echo "✅ Database reset complete"

clean:
	docker-compose down -v

shell:
	docker-compose run --rm pipeline /bin/bash

test:
	docker-compose run --rm pipeline python -m pytest tests/

process-summaries:
	@echo "🔄 Processing summaries for papers..."
	@docker-compose run --rm pipeline python scripts/process_summaries.py

web:
	@echo "🌐 Starting web interface..."
	@docker-compose up -d web
	@echo "Web interface running at http://localhost:8000"

web-logs:
	docker-compose logs -f web
