# Classic Models API - Simplified Makefile

.PHONY: build start stop health-check test help

# Default target
.DEFAULT_GOAL := help

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Classic Models API - Available Commands$(NC)"
	@echo ""
	@echo "  $(GREEN)build$(NC)        - Build the Docker containers"
	@echo "  $(GREEN)start$(NC)        - Start the containers (database resets to original data)"
	@echo "  $(GREEN)stop$(NC)         - Stop the containers"
	@echo "  $(GREEN)test$(NC)         - Run the test suite"
	@echo "  $(GREEN)health-check$(NC) - Run health check against the API endpoints"
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make build        # Build containers"
	@echo "  make start        # Start with fresh database"
	@echo "  make test         # Run all tests"
	@echo "  make health-check # Check if API is working"

build: ## Build the Docker containers
	@echo "$(BLUE)Building Docker containers...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Containers built successfully$(NC)"

start: ## Start the containers (database resets to original data)
	@echo "$(BLUE)Starting containers with fresh database...$(NC)"
	docker-compose down -v
	docker-compose up -d
	@echo "$(GREEN)✓ Containers started with fresh database$(NC)"
	@echo "$(YELLOW)API available at: http://localhost:8000$(NC)"

stop: ## Stop the containers
	@echo "$(BLUE)Stopping containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Containers stopped$(NC)"

test: ## Run the test suite
	@echo "$(BLUE)Running test suite...$(NC)"
	pytest
	@echo "$(GREEN)✓ All tests completed$(NC)"

health-check: ## Run health check against the API endpoints
	@echo "$(BLUE)Running health check...$(NC)"
	@echo "Checking API endpoints..."
	@curl -f -s http://localhost:8000/api/docs/ > /dev/null && echo "$(GREEN)✓ API documentation is available$(NC)" || echo "$(RED)✗ API documentation is not available$(NC)"
	@curl -f -s http://localhost:8000/api/schema/ > /dev/null && echo "$(GREEN)✓ API schema is available$(NC)" || echo "$(RED)✗ API schema is not available$(NC)"
	@curl -f -s -w "%{http_code}" -o /dev/null http://localhost:8000/api/auth/register/ | grep -q "405" && echo "$(GREEN)✓ Authentication endpoints are responding$(NC)" || echo "$(RED)✗ Authentication endpoints are not responding$(NC)"
	@curl -f -s -w "%{http_code}" -o /dev/null http://localhost:8000/api/v1/classicmodels/customers/ | grep -q "401\|403" && echo "$(GREEN)✓ Customers endpoint is responding (authentication required)$(NC)" || echo "$(RED)✗ Customers endpoint is not responding$(NC)"
	@curl -f -s -w "%{http_code}" -o /dev/null http://localhost:8000/api/v1/classicmodels/products/ | grep -q "401\|403" && echo "$(GREEN)✓ Products endpoint is responding (authentication required)$(NC)" || echo "$(RED)✗ Products endpoint is not responding$(NC)"
	@echo "$(GREEN)✓ Health check completed$(NC)"