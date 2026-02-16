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

The unified CLI is `mms` with subcommands:

```
mms worker         - Main media processing worker
mms clean          - Clean up media files
mms index          - Index media files to MongoDB
mms inventory scan - Scan Jellyfin libraries + watch activity, push to Prometheus
mms download subsplease - Download anime from SubsPlease
mms download erai  - Download anime from Erai-raws
mms sg worker      - SuicideGirls download worker
mms sg scrape      - SuicideGirls scraper
```

Legacy standalone entry points also exist: `media-worker`, `subsplease-dl`, `media-cleaner`, `media-indexer`, `sg-worker`, `sg-scrape`.

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

- `cli/` - Click command groups: `main.py` (unified `mms` entry), `inventory.py`, etc.
- `config.py` - Centralized env-var config (MongoDB, Jellyfin, Pushgateway, LLM, paths)
- `db/` - MongoDB connection (`mongo.py`) and indexing (`indexer.py`)
- `download/` - Image downloads (`images.py`), magnet handling (`magnets.py`), Transmission client (`transmission.py`)
- `organize/` - File parsing (`parse.py`), classification (`classify.py`), movement (`mover.py`)
- `sources/` - Jellyfin API client (`jellyfin.py`), Prometheus Pushgateway (`prometheus.py`), SubsPlease, Erai-raws, SuicideGirls
- `util/` - File utilities and Ollama LLM integration (`ollama.py`)

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

## Monitoring & Inventory

`mms inventory scan --push-metrics` queries the Jellyfin API and pushes gauge metrics to Prometheus Pushgateway. Prometheus scrapes the Pushgateway; Grafana renders the "Media Library Inventory" dashboard.

### Pipeline

```
Jellyfin API  →  mms inventory scan  →  Pushgateway (:9091)  →  Prometheus  →  Grafana
```

### Metrics (two Pushgateway jobs)

**`media_inventory`** - library counts:
- `mms_inventory_anime_titles`, `mms_inventory_anime_episodes`
- `mms_inventory_movie_titles`
- `mms_inventory_show_titles`, `mms_inventory_show_episodes`
- `mms_inventory_last_scan_timestamp`

**`media_activity`** - watch activity (requires `JELLYFIN_USER_ID`):
- `mms_activity_episodes_watched_7d`, `mms_activity_episodes_watched_30d`
- `mms_activity_total_played`, `mms_activity_continue_watching`
- `mms_activity_resume_item{series="...", episode="..."}` - labeled gauge, value = watch percentage

### Grafana Dashboard

Dashboard UID: `d952e8a8-79df-4186-b656-b03ebf032042` ("Media Library Inventory")

- Stat panels use `instant: true` queries (required for Pushgateway gauges)
- Continue Watching table uses `mms_activity_resume_item` with `format: table` + `organize` transform
- Dashboard is managed via Grafana HTTP API (`POST /api/dashboards/db`); Grafana port 3000 is **not** mapped to host (use `docker exec grafana wget` to update)

### Infrastructure (all on 10.0.0.12, Docker network)

All containers share one Docker network: `prometheus`, `pushgateway`, `grafana`, `jellyfin`, `loki`, `promtail`, `node-exporter`, `cadvisor`, `mongo`, `traefik`.

- Pushgateway: port 9091 mapped to host (reachable externally)
- Prometheus: port 9090 **not** mapped (internal only, query via `docker exec`)
- Grafana: port 3000 **not** mapped (access via Traefik or `docker exec`)
- Prometheus scrapes pushgateway every 15s with `honor_labels: true`

### Environment Variables for Inventory

| Variable | Default | Notes |
|---|---|---|
| `JELLYFIN_URL` | `http://10.0.0.12:8096` | |
| `JELLYFIN_API_KEY` | (none) | Required; stored in swamp vault `homelab/jellyfin-api-key` |
| `JELLYFIN_USER_ID` | (none) | Optional; defaults to first user. Set to target a specific user for activity. |
| `PUSHGATEWAY_URL` | `http://10.0.0.12:9091` | |

### Swamp Integration

The `inventory-scan` swamp model (`.swamp/definitions/command/shell/f6532e0c-...`) runs the scan with vault-resolved credentials. It sets `JELLYFIN_USER_ID` to keeb's ID.

## Key Patterns

- **MongoDB**: Primary data store (default: `10.0.0.12:27017`, database: `media`)
- **Environment config**: Use `MONGO_HOST` and `MONGO_DATABASE` env vars (see `run-llm` wrapper)
- **LLM integration**: `prompts/` directory contains prompts for filename parsing via Ollama
- **File classification**: Anime vs movies vs regular files detected via patterns in `organize/classify.py`
