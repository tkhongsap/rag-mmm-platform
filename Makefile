PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)

.PHONY: install test test-rag test-mmm lint run-app run-rag-cli clean help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	$(PYTHON) -m pip install -r requirements.txt

test: ## Run all tests
	$(PYTHON) -m pytest tests/ -v

test-rag: ## Run RAG tests only
	$(PYTHON) -m pytest tests/rag/ -v

test-mmm: ## Run MMM tests only
	$(PYTHON) -m pytest tests/mmm/ -v

test-cov: ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

lint: ## Run linting checks
	$(PYTHON) -m py_compile src/rag/__init__.py
	$(PYTHON) -m py_compile src/mmm/__init__.py

run-app: ## Launch React platform app (http://localhost:3001)
	cd ui/platform && npm run dev

run-rag-cli: ## Run RAG retrieval CLI in interactive mode
	$(PYTHON) -m src.rag.retrieval.cli --interactive

clean: ## Remove generated artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/
