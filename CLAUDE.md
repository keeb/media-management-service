# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python Setup

```bash
# Create and activate virtual environment
uv venv && source .venv/bin/activate

# Install package in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/

# Run specific test
pytest tests/parse_test.py
```

### CLI Commands (after installation)

The package exposes these CLI commands:

- `media-worker` - Main media processing worker (use `run-llm` wrapper for configured env vars)
- `subsplease-dl` - Download anime from SubsPlease
- `media-cleaner` - Clean up media files
- `media-indexer` - Index media files to MongoDB
- `sg-worker` - SuicideGirls download worker
- `sg-scrape` - SuicideGirls scraper

### Go Services

```bash
cd go/subsplease-rss
go build -o subsplease-rss-to-json
./subsplease-rss-to-json
```

### Individual Services

Each service in `services/` is independent:

- **Go services**: `go build && ./service-name` or `go run main.go`
- **Python services**: `python main.py` or service-specific `run.sh`
- **Docker services**: `docker build -t service-name .`

## Architecture Overview

**Monorepo** containing multiple independent, loosely-coupled services. Do not assume cohesive integration between components.

### Python Package (`python/src/mediaservice/`)

Core library with domain-organized modules:

- `cli/` - Command-line entry points for each tool
- `db/` - MongoDB connection (`mongo.py`) and indexing (`indexer.py`)
- `download/` - Image downloads (`images.py`) and Transmission client (`transmission.py`)
- `organize/` - File parsing (`parse.py`), classification (`classify.py`), movement (`mover.py`), filtering (`filter.py`)
- `sources/` - Content source integrations (SubsPlease, SuicideGirls)
- `util/` - File utilities and Ollama LLM integration

### Go Services (`go/`)

Standalone Go modules:

- `subsplease-rss/` - Converts SubsPlease RSS to JSON

### Legacy Services (`services/`)

21 independent microservices (mixed Python/Go/Docker):

- **RSS converters**: `eztv-rss-to-json`, `subsplease-rss-to-json`
- **APIs**: `go-eztv-api`, `sg-scrape-api`
- **Torrent handling**: `container-magnet`, `transmission-magnet-uri-downloader`
- **File management**: `watcher`, `mover`, `mongo-dedup`
- **Platform magnet launchers**: `linux-magnet-launcher`, `windows-magnet-launcher`

### Systemd Units (`units/`)

Service/timer pairs for automated anime downloads (dandadan, gachiakuta, etc.)

## Data Flow

1. RSS feeds parsed to JSON by Go services
2. `subsplease-dl` or workers download content
3. `media-worker` processes and organizes files using `organize/` modules
4. Completed items tracked in MongoDB (`db.pending` → `db.completed`)
5. Web interface (`scripts/main-web.py`) serves content

## Key Patterns

- **MongoDB**: Primary data store (default: `10.0.0.12:27017`, database: `media`)
- **Environment config**: Use `MONGO_HOST` and `MONGO_DATABASE` env vars (see `run-llm` wrapper)
- **LLM integration**: `prompts/` directory contains prompts for filename parsing via Ollama
- **File classification**: Anime vs movies vs regular files detected via patterns in `organize/classify.py`
