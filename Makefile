# Classic Models API Makefile
# This Makefile provides convenient commands for development, testing, and deployment

.PHONY: help install install-dev test test-coverage test-unit test-api test-models lint format clean run migrate makemigrations shell superuser load-data build up down logs restart status

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
MANAGE := $(PYTHON) manage.py
DOCKER_COMPOSE := docker-compose
DOCKER := docker

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Classic Models API - Available Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make install     # Install dependencies"
	@echo "  make test        # Run all tests"
	@echo "  make run         # Start development server"
	@echo "  make docker-up   # Start with Docker"

# Installation Commands
install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-django pytest-cov coverage black isort flake8
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

# Database Commands
migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	$(MANAGE) migrate
	@echo "$(GREEN)✓ Migrations completed$(NC)"

makemigrations: ## Create new database migrations
	@echo "$(BLUE)Creating new migrations...$(NC)"
	$(MANAGE) makemigrations
	@echo "$(GREEN)✓ Migrations created$(NC)"

migrate-reset: ## Reset and apply all migrations
	@echo "$(BLUE)Resetting database migrations...$(NC)"
	rm -f db.sqlite3
	$(MANAGE) makemigrations
	$(MANAGE) migrate
	@echo "$(GREEN)✓ Database reset and migrations applied$(NC)"

# Development Commands
run: ## Start development server
	@echo "$(BLUE)Starting development server...$(NC)"
	$(MANAGE) runserver

run-prod: ## Start production server
	@echo "$(BLUE)Starting production server...$(NC)"
	$(MANAGE) runserver 0.0.0.0:8000

shell: ## Open Django shell
	@echo "$(BLUE)Opening Django shell...$(NC)"
	$(MANAGE) shell

superuser: ## Create Django superuser
	@echo "$(BLUE)Creating Django superuser...$(NC)"
	$(MANAGE) createsuperuser

load-data: ## Load sample data
	@echo "$(BLUE)Loading sample data...$(NC)"
	$(PYTHON) create_demo_user.py
	@echo "$(GREEN)✓ Sample data loaded$(NC)"

# Testing Commands
test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	pytest tests/ -v
	@echo "$(GREEN)✓ All tests completed$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/test_models/ -v
	@echo "$(GREEN)✓ Unit tests completed$(NC)"

test-api: ## Run API tests only
	@echo "$(BLUE)Running API tests...$(NC)"
	pytest tests/test_api/ -v
	@echo "$(GREEN)✓ API tests completed$(NC)"

test-models: ## Run model tests only
	@echo "$(BLUE)Running model tests...$(NC)"
	pytest tests/test_models/ -v
	@echo "$(GREEN)✓ Model tests completed$(NC)"

test-fast: ## Run fast tests (exclude slow tests)
	@echo "$(BLUE)Running fast tests...$(NC)"
	pytest tests/ -v -m "not slow"
	@echo "$(GREEN)✓ Fast tests completed$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	pytest-watch tests/

# Code Quality Commands
lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	flake8 . --exclude=migrations,venv,env,.venv
	@echo "$(GREEN)✓ Linting completed$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black . --exclude="migrations|venv|env|.venv"
	isort . --skip migrations --skip venv --skip env --skip .venv
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	black . --check --exclude="migrations|venv|env|.venv"
	isort . --check-only --skip migrations --skip venv --skip env --skip .venv
	@echo "$(GREEN)✓ Code formatting check completed$(NC)"

# Docker Commands
build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Docker images built$(NC)"

up: ## Start services with Docker Compose
	@echo "$(BLUE)Starting services with Docker Compose...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Services started$(NC)"

down: ## Stop services with Docker Compose
	@echo "$(BLUE)Stopping services with Docker Compose...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart services with Docker Compose
	@echo "$(BLUE)Restarting services with Docker Compose...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

logs: ## View Docker Compose logs
	@echo "$(BLUE)Viewing Docker Compose logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f

logs-api: ## View API service logs
	@echo "$(BLUE)Viewing API service logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f api

logs-db: ## View database service logs
	@echo "$(BLUE)Viewing database service logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f db

status: ## Show Docker Compose service status
	@echo "$(BLUE)Docker Compose service status:$(NC)"
	$(DOCKER_COMPOSE) ps

# Database Commands (Docker)
db-migrate: ## Run migrations in Docker container
	@echo "$(BLUE)Running migrations in Docker container...$(NC)"
	$(DOCKER_COMPOSE) exec api $(MANAGE) migrate
	@echo "$(GREEN)✓ Migrations completed$(NC)"

db-shell: ## Open database shell in Docker container
	@echo "$(BLUE)Opening database shell...$(NC)"
	$(DOCKER_COMPOSE) exec db mysql -u root -pclassicmodels classicmodels

db-backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	$(DOCKER_COMPOSE) exec db mysqldump -u root -pclassicmodels classicmodels > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up$(NC)"

db-restore: ## Restore database from backup (usage: make db-restore FILE=backup.sql)
	@echo "$(BLUE)Restoring database from $(FILE)...$(NC)"
	$(DOCKER_COMPOSE) exec -T db mysql -u root -pclassicmodels classicmodels < $(FILE)
	@echo "$(GREEN)✓ Database restored$(NC)"

# Development Setup Commands
setup: install-dev migrate load-data ## Complete development setup
	@echo "$(GREEN)✓ Development environment setup complete$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Run 'make run' to start the development server"
	@echo "  2. Visit http://localhost:8000/api/v1/ to see the API"
	@echo "  3. Run 'make test' to run the test suite"

setup-docker: build up db-migrate ## Complete Docker setup
	@echo "$(GREEN)✓ Docker environment setup complete$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Visit http://localhost:8000/api/v1/ to see the API"
	@echo "  2. Run 'make test' to run the test suite"
	@echo "  3. Run 'make logs' to view service logs"

# Testing in Docker
test-docker: ## Run tests in Docker container
	@echo "$(BLUE)Running tests in Docker container...$(NC)"
	$(DOCKER_COMPOSE) exec api pytest tests/ -v
	@echo "$(GREEN)✓ Tests completed in Docker$(NC)"

test-coverage-docker: ## Run tests with coverage in Docker container
	@echo "$(BLUE)Running tests with coverage in Docker container...$(NC)"
	$(DOCKER_COMPOSE) exec api pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated$(NC)"

# Documentation Commands
docs: ## Generate API documentation
	@echo "$(BLUE)Generating API documentation...$(NC)"
	$(MANAGE) spectacular --file schema.yml
	@echo "$(GREEN)✓ API documentation generated$(NC)"

docs-serve: ## Serve API documentation
	@echo "$(BLUE)Serving API documentation...$(NC)"
	$(MANAGE) runserver 8001 &
	@echo "$(YELLOW)API documentation available at http://localhost:8001/api/schema/swagger-ui/$(NC)"

# Security Commands
security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	$(PIP) install safety bandit
	safety check
	bandit -r . -x tests/
	@echo "$(GREEN)✓ Security checks completed$(NC)"

# Performance Commands
profile: ## Run performance profiling
	@echo "$(BLUE)Running performance profiling...$(NC)"
	$(PIP) install django-debug-toolbar
	@echo "$(YELLOW)Add django-debug-toolbar to INSTALLED_APPS for profiling$(NC)"

# Cleanup Commands
clean: ## Clean up temporary files and caches
	@echo "$(BLUE)Cleaning up temporary files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -f db.sqlite3
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

clean-docker: ## Clean up Docker containers and images
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f
	@echo "$(GREEN)✓ Docker cleanup completed$(NC)"

# Deployment Commands
deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@echo "$(YELLOW)Add your staging deployment commands here$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(NC)"
	@echo "$(YELLOW)Add your production deployment commands here$(NC)"

# Monitoring Commands
health-check: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	curl -f http://localhost:8000/api/v1/ || echo "$(RED)✗ API is not responding$(NC)"
	@echo "$(GREEN)✓ Health check completed$(NC)"

# Database Management
db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		$(MAKE) migrate-reset; \
		$(MAKE) load-data; \
		echo "$(GREEN)✓ Database reset completed$(NC)"; \
	else \
		echo ""; \
		echo "$(YELLOW)Database reset cancelled$(NC)"; \
	fi

# Quick Commands
quick-test: ## Quick test run (fast tests only)
	@echo "$(BLUE)Running quick tests...$(NC)"
	pytest tests/ -v -m "not slow" --tb=short
	@echo "$(GREEN)✓ Quick tests completed$(NC)"

quick-start: ## Quick start for new developers
	@echo "$(BLUE)Quick start setup...$(NC)"
	$(MAKE) install-dev
	$(MAKE) migrate
	$(MAKE) load-data
	@echo "$(GREEN)✓ Quick start completed$(NC)"
	@echo "$(YELLOW)Run 'make run' to start the development server$(NC)"

# Version Commands
version: ## Show version information
	@echo "$(BLUE)Version Information:$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Django: $$($(PYTHON) -c 'import django; print(django.get_version())')"
	@echo "Docker: $$($(DOCKER) --version)"
	@echo "Docker Compose: $$($(DOCKER_COMPOSE) --version)"

# Environment Commands
env-check: ## Check environment setup
	@echo "$(BLUE)Checking environment setup...$(NC)"
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "$(RED)✗ Python not found$(NC)"; exit 1; }
	@command -v $(PIP) >/dev/null 2>&1 || { echo "$(RED)✗ pip not found$(NC)"; exit 1; }
	@command -v $(DOCKER) >/dev/null 2>&1 || { echo "$(YELLOW)⚠ Docker not found (optional)$(NC)"; }
	@command -v $(DOCKER_COMPOSE) >/dev/null 2>&1 || { echo "$(YELLOW)⚠ Docker Compose not found (optional)$(NC)"; }
	@echo "$(GREEN)✓ Environment check completed$(NC)"

# All-in-one Commands
ci: lint test-coverage security-check ## Run CI pipeline locally
	@echo "$(GREEN)✓ CI pipeline completed$(NC)"

dev: setup run ## Complete development workflow
	@echo "$(GREEN)✓ Development workflow completed$(NC)"

prod: build up db-migrate ## Complete production setup
	@echo "$(GREEN)✓ Production setup completed$(NC)"
