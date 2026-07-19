.PHONY: init run clean help lint test setup engine bot-test

# Variables
PYTHON := python3
PIP := pip3

help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║     UOS-Core Multi-Node Automation System - Commands         ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  make init       - Initialize system configuration"
	@echo "  make run        - Execute task orchestrator"
	@echo "  make engine     - Run UOS Engine with multi-node support"
	@echo "  make bot-test   - Test bot manager and nodes"
	@echo "  make setup      - Install dependencies and setup"
	@echo "  make lint       - Run code linting checks"
	@echo "  make test       - Run tests (if available)"
	@echo "  make clean      - Clean generated files and cache"
	@echo "  make help       - Display this help message"
	@echo ""

setup:
	@echo "📦 Setting up UOS-Core environment..."
	@$(PIP) install python-dotenv
	@$(PIP) install python-telegram-bot
	@$(PIP) install google-generativeai
	@echo "✓ Dependencies installed"

init:
	@echo "🔧 Initializing system configuration..."
	@$(PYTHON) initialize_project.py
	@echo "✓ Initialization completed"

run: init
	@echo "🚀 Starting task orchestrator..."
	@$(PYTHON) task_orchestrator.py
	@echo "✓ Orchestrator execution completed"

engine: init
	@echo "🚀 Starting UOS Engine with multi-node support..."
	@$(PYTHON) uos_engine.py
	@echo "✓ UOS Engine execution completed"

bot-test: init
	@echo "🤖 Testing Bot Manager and multi-node system..."
	@$(PYTHON) bot_manager.py
	@echo "✓ Bot Manager test completed"

lint:
	@echo "🔍 Running code linting checks..."
	@if command -v pylint &> /dev/null; then \
		$(PYTHON) -m pylint initialize_project.py task_orchestrator.py uos_engine.py bot_manager.py --exit-zero || true; \
	else \
		echo "⚠ pylint not installed. Attempting with flake8..."; \
		$(PYTHON) -m flake8 initialize_project.py task_orchestrator.py uos_engine.py bot_manager.py 2>/dev/null || echo "⚠ flake8 not found"; \
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
