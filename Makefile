# Makefile for Rodent AI Vision Box
# Professional build automation

.PHONY: help clean test install dev-install lint format type-check security-check build deploy docs

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PROJECT_NAME := rodent-ai-vision-box
VENV := venv
SOURCE_DIR := src
TEST_DIR := tests
DOC_DIR := docs

# Colors for terminal output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Rodent AI Vision Box - Development Commands$(NC)"
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(YELLOW)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev-install: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"
	pre-commit install
	@echo "$(GREEN)✓ Development environment ready$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(YELLOW)Cleaning project...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Project cleaned$(NC)"

format: ## Format code with black and isort
	@echo "$(YELLOW)Formatting code...$(NC)"
	black $(SOURCE_DIR) tests scripts --line-length 100
	isort $(SOURCE_DIR) tests scripts
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Run linting checks
	@echo "$(YELLOW)Running linters...$(NC)"
	flake8 $(SOURCE_DIR) --max-line-length=100 --ignore=E203,W503
	pylint $(SOURCE_DIR)
	@echo "$(GREEN)✓ Linting passed$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(YELLOW)Running type checks...$(NC)"
	mypy $(SOURCE_DIR) --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking passed$(NC)"

security-check: ## Run security checks
	@echo "$(YELLOW)Running security checks...$(NC)"
	bandit -r $(SOURCE_DIR)
	safety check
	@echo "$(GREEN)✓ Security checks passed$(NC)"

test: ## Run all tests with coverage
	@echo "$(YELLOW)Running tests...$(NC)"
	pytest tests/ -v --cov=$(SOURCE_DIR) --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Tests completed$(NC)"

test-unit: ## Run unit tests only
	@echo "$(YELLOW)Running unit tests...$(NC)"
	pytest tests/unit -v
	@echo "$(GREEN)✓ Unit tests completed$(NC)"

test-integration: ## Run integration tests
	@echo "$(YELLOW)Running integration tests...$(NC)"
	pytest tests/integration -v
	@echo "$(GREEN)✓ Integration tests completed$(NC)"

build: clean ## Build distribution packages
	@echo "$(YELLOW)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Build completed$(NC)"

deploy-prepare: ## Prepare deployment package
	@echo "$(YELLOW)Preparing deployment package...$(NC)"
	mkdir -p dist/$(PROJECT_NAME)
	cp -r src models config scripts dist/$(PROJECT_NAME)/
	cp requirements.txt setup.* *.md .env.example dist/$(PROJECT_NAME)/
	cd dist && tar -czf $(PROJECT_NAME)-v1.0.0.tar.gz $(PROJECT_NAME)
	@echo "$(GREEN)✓ Deployment package ready: dist/$(PROJECT_NAME)-v1.0.0.tar.gz$(NC)"

deploy-raspberry: ## Deploy to Raspberry Pi (requires PI_HOST environment variable)
	@if [ -z "$(PI_HOST)" ]; then \
		echo "$(RED)Error: PI_HOST environment variable not set$(NC)"; \
		echo "Usage: PI_HOST=pi@192.168.1.100 make deploy-raspberry"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Deploying to Raspberry Pi at $(PI_HOST)...$(NC)"
	scp dist/$(PROJECT_NAME)-v1.0.0.tar.gz $(PI_HOST):/home/pi/
	ssh $(PI_HOST) "cd /home/pi && tar -xzf $(PROJECT_NAME)-v1.0.0.tar.gz && cd $(PROJECT_NAME) && sudo bash setup.sh"
	@echo "$(GREEN)✓ Deployed to Raspberry Pi$(NC)"

docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	cd docs && $(MAKE) html
	@echo "$(GREEN)✓ Documentation generated in docs/_build/html$(NC)"

serve-docs: ## Serve documentation locally
	@echo "$(YELLOW)Serving documentation at http://localhost:8000$(NC)"
	cd docs/_build/html && $(PYTHON) -m http.server

monitor: ## Monitor system logs (for deployed system)
	@echo "$(YELLOW)Monitoring rodent detection logs...$(NC)"
	journalctl -u rodent-detection -f

check-all: lint type-check security-check test ## Run all checks
	@echo "$(GREEN)✓ All checks passed!$(NC)"

setup-venv: ## Create and setup virtual environment
	@echo "$(YELLOW)Setting up virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install --upgrade pip
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Virtual environment ready. Activate with: source $(VENV)/bin/activate$(NC)"

docker-build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(YELLOW)Running Docker container...$(NC)"
	docker run -d --name $(PROJECT_NAME) \
		--device /dev/video0 \
		-v $(PWD)/config:/app/config \
		-v $(PWD)/data:/app/data \
		--env-file .env \
		$(PROJECT_NAME):latest
	@echo "$(GREEN)✓ Container running$(NC)"

version: ## Show version information
	@echo "$(BLUE)Rodent AI Vision Box$(NC)"
	@echo "Version: 1.0.0"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Model: YOLOv8 (ONNX)"

.DEFAULT_GOAL := help