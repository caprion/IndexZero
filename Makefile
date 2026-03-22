# IndexZero — Makefile
# Targets use the .venv in the project root.
# Works on Linux, macOS, and Windows (via Git Bash / WSL / make for Windows).

VENV   := .venv
PYTHON := $(VENV)/Scripts/python
PIP    := $(VENV)/Scripts/pip

# Detect Unix-style paths (Linux / macOS / WSL)
ifeq ($(OS),Windows_NT)
	PYTHON := $(VENV)/Scripts/python
	PIP    := $(VENV)/Scripts/pip
else
	PYTHON := $(VENV)/bin/python
	PIP    := $(VENV)/bin/pip
endif

.PHONY: setup test lint clean help

help: ## Show this help
	@echo IndexZero targets:
	@echo   make setup  - Create venv and install in editable mode
	@echo   make test   - Run pytest
	@echo   make lint   - Run ruff (if installed)
	@echo   make clean  - Remove build artifacts

setup: ## Create venv, upgrade pip, install package in editable mode
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo ""
	@echo "Done. Activate with:"
	@echo "  Windows PowerShell:  .venv\Scripts\Activate.ps1"
	@echo "  Linux / macOS:       source .venv/bin/activate"

test: ## Run all tests with pytest
	$(PYTHON) -m pytest tests/ -v

lint: ## Run ruff linter (install ruff first: pip install ruff)
	$(PYTHON) -m ruff check src/ tests/

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
