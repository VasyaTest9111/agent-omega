.PHONY: init run clean help lint test

# Variables
PYTHON := python3
PIP := pip3

help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║          UOS-Core Automation System - Commands               ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  make init      - Initialize system configuration"
	@echo "  make run       - Execute task orchestrator"
	@echo "  make lint      - Run code linting checks"
	@echo "  make test      - Run tests (if available)"
	@echo "  make clean     - Clean generated files and cache"
	@echo "  make help      - Display this help message"
	@echo ""

init:
	@echo "🔧 Initializing UOS-Core system configuration..."
	@$(PYTHON) initialize_project.py
	@echo "✓ Initialization completed"

run: init
	@echo "🚀 Starting task orchestrator..."
	@$(PYTHON) task_orchestrator.py
	@echo "✓ Orchestrator execution completed"

lint:
	@echo "🔍 Running code linting checks..."
	@if command -v pylint &> /dev/null; then \
		$(PYTHON) -m pylint initialize_project.py task_orchestrator.py --exit-zero || true; \
	else \
		echo "⚠ pylint not installed. Attempting with flake8..."; \
		$(PYTHON) -m flake8 initialize_project.py task_orchestrator.py 2>/dev/null || echo "⚠ flake8 not found"; \
	fi
	@echo "✓ Linting checks completed"

test:
	@echo "🧪 Running tests..."
	@if [ -f "test_*.py" ] || [ -f "tests/*.py" ]; then \
		$(PYTHON) -m pytest -v; \
	else \
		echo "⚠ No test files found"; \
	fi

clean:
	@echo "🧹 Cleaning generated files..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -f SYSTEM_CONFIG.py
	@echo "✓ Cleanup completed"

.DEFAULT_GOAL := help
