# Default goal
DEFAULT_GOAL := help

# Use uv by default; override with `make PYRUN="python -m"`
PYRUN ?= uv run
TEST_DIR ?= tests
TEST_PATTERN ?= test_*.py

.PHONY: help lint lint-fix format format-check fix test sync

help:
	@echo "Available targets:"
	@echo "  sync           - Sync dependencies using uv"
	@echo "  lint           - Run ruff lint checks"
	@echo "  lint-fix       - Run ruff and auto-fix issues where possible"
	@echo "  format         - Format code using ruff formatter"
	@echo "  format-check   - Check formatting without changing files"
	@echo "  fix            - Apply lint fixes and then format"
	@echo "  test           - Run unit tests in '$(TEST_DIR)' (supports FILE/TEST/FUNC)"
	@echo ""
	@echo "Examples:"
	@echo "  make lint"
	@echo "  make format"
	@echo "  make fix"
	@echo "  make test"
	@echo "  make test FILE=test_example.py"
	@echo "  make test TEST=test_example.py::TestClass::test_func"
	@echo "  make test FUNC=test_specific_function"
	@echo ""
	@echo "Notes:"
	@echo "  - Uses '$(PYRUN)' to run tools (defaults to 'uv run')."
	@echo "  - If not using uv, run: make PYRUN=\"python -m\" <target>"

lint:
	$(PYRUN) ruff check .

lint-fix:
	$(PYRUN) ruff check . --fix

format:
	$(PYRUN) ruff format .

format-check:
	$(PYRUN) ruff format . --check

fix: lint-fix format

test:
	$(PYRUN) pytest $(if $(TEST),$(TEST_DIR)/$(TEST),$(if $(FILE),$(TEST_DIR)/$(FILE),$(TEST_DIR)/)) $(if $(FUNC),-k "$(FUNC)",) -v -s -o log_cli=true -o log_cli_level=INFO -W ignore::DeprecationWarning

sync:
	uv sync

build:
	uv --no-cache build

publish:
	uv publish

publish-test:
	uv publish --publish-url https://test.pypi.org/legacy/