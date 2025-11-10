# Default goal
DEFAULT_GOAL := help

# Use uv by default; override with `make PYRUN="python -m"`
PYRUN ?= uv run

.PHONY: help lint lint-fix format format-check fix

help:
	@echo "Available targets:"
	@echo "  lint           - Run ruff lint checks"
	@echo "  lint-fix       - Run ruff and auto-fix issues where possible"
	@echo "  format         - Format code using ruff formatter"
	@echo "  format-check   - Check formatting without changing files"
	@echo "  fix            - Apply lint fixes and then format"
	@echo ""
	@echo "Examples:"
	@echo "  make lint"
	@echo "  make format"
	@echo "  make fix"
	@echo ""
	@echo "Notes:"
	@echo "  - Uses '$(PYRUN)' to run tools (defaults to 'uv run')."
	@echo "  - If not using uv, run: make PYRUN=\"python -m\" lint"

lint:
	$(PYRUN) ruff check .

lint-fix:
	$(PYRUN) ruff check . --fix

format:
	$(PYRUN) ruff format .

format-check:
	$(PYRUN) ruff format . --check

fix: lint-fix format