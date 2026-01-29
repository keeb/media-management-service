# Makefile for Media Management Service

.PHONY: help install install-build build clean test dev

help:
	@echo "Media Management Service - Build Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install package in editable mode with dev deps"
	@echo "  make install-build - Install package with build dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Run mms CLI in development mode"
	@echo "  make test          - Run tests"
	@echo ""
	@echo "Build:"
	@echo "  make build         - Build single binary (dist/mms)"
	@echo "  make clean         - Clean build artifacts"
	@echo ""
	@echo "Install:"
	@echo "  make install-bin   - Install binary to /usr/local/bin (requires sudo)"

# Setup virtual environment and install dependencies
install:
	uv venv
	. .venv/bin/activate && uv pip install -e ".[dev]"

install-build:
	uv venv
	. .venv/bin/activate && uv pip install -e ".[dev,build]"

# Run CLI in development mode
dev:
	uv run mms --help

# Run tests
test:
	uv run pytest tests/

# Build single binary
build:
	uv run python packaging/build.py

# Clean build artifacts
clean:
	rm -rf packaging/__pycache__
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf python/src/*.egg-info
	rm -rf .pytest_cache

# Install binary system-wide
install-bin: build
	@echo "Installing mms to /usr/local/bin..."
	sudo cp dist/mms /usr/local/bin/mms
	sudo chmod +x /usr/local/bin/mms
	@echo "Done. Run 'mms --help' to verify."
