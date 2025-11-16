# Makefile
.PHONY: help install dev test clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Run development server"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up generated files"
	@echo "  make docker-up   - Start Docker services"
	@echo "  make docker-down - Stop Docker services"

install:
	pip install -r requirements.txt
	python scripts/init_db.py

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api
