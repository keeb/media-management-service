# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python Environment

- Activate virtual environment: `source env/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Run tests: `python -m unittest test/parse_test.py`

### Individual Services

Each service in `services/` has its own build/run commands:

- Go services: Use `go build` then `./service-name` or `go run main.go`
- Python services: Run directly with `python main.py` or use service-specific `run.sh` scripts
- Services with Dockerfiles: Build with `docker build -t service-name .`

### Common Scripts

- Run web interface: `python scripts/main-web.py` (Flask app on port 5000)
- Run worker: `python scripts/worker.py` (processes MongoDB queue)
- Clear queue: `scripts/clear_queue.sh`
- File filtering: `python scripts/filter.py`

## Architecture Overview

**IMPORTANT**: This is a monorepo containing multiple independent, loosely-coupled services and scripts. Do not assume cohesive integration between components - each service/script may have different dependencies, build processes, and purposes. The shared `lib/` directory provides common utilities, but services are designed to operate independently.

Current structure (needs improvement):

### Core Library (`lib/`)

- `mongo.py`: MongoDB connection and collections (pending queue, completed jobs)
- `payload.py`: Data structure for SuicideGirls scraping jobs with sanitization
- `media.py`: Media file classification (anime detection, movie parsing)
- `parse.py`: Filename parsing utilities
- `filter.py`: Content filtering logic
- `suicidegirls.py`: SuicideGirls-specific data structures
- `transmission.py`: BitTorrent client integration

### Scripts (`scripts/`)

Main execution scripts that use the core library:

- `worker.py`: Downloads images from queued jobs, moves from pending to completed
- `main-web.py`: Flask web interface for browsing downloaded images
- `filter.py`: Media file organization and filtering
- `scrape.py`: SuicideGirls content scraping

### Services (`services/`)

Independent microservices for specific tasks:

- **RSS to JSON converters**: `eztv-rss-to-json`, `subsplease-rss-to-json` (Go)
- **API services**: `go-eztv-api` (torrent data), `sg-scrape-api` (Python/Flask)
- **Torrent handling**: `container-magnet` (libtorrent), `transmission-magnet-uri-downloader`
- **File management**: `watcher`, `mover`, `mongo-dedup`
- **Platform-specific**: `windows-magnet-launcher`, `linux-magnet-launcher`

### Data Flow

1. Scraping jobs are queued in MongoDB (`db.pending`)
2. Worker processes download images and organize by model/album structure
3. Completed jobs moved to `db.completed` collection
4. Web interface serves images from `static/img/` directory
5. RSS services convert torrent feeds to JSON for automation

## Key Patterns

- MongoDB is primary data store (connection: `treehouse.local:27017`)
- Payload objects handle data sanitization (spaces→hyphens, lowercase)  
- Media files classified by format detection (anime vs movies vs regular files)
- Services are containerized where applicable (Dockerfiles present)
- Go services use modules and follow standard Go project structure
- Python code uses virtual environment in `env/`

## Proposed Improved Structure

The current structure mixes scripts, services, and libraries without clear domain separation. Here's a suggested reorganization:

```
media-management-service/
├── core/                           # Shared libraries and utilities
│   ├── python-lib/                 # Current lib/ contents
│   │   ├── mongo.py
│   │   ├── payload.py
│   │   ├── media.py
│   │   └── ...
│   └── go-lib/                     # Shared Go modules (if needed)
├── media-processing/               # Image/video handling services
│   ├── sg-worker/                  # Current scripts/worker.py
│   ├── sg-scraper/                 # Current scripts/scrape.py + sg-scrape-api
│   ├── media-organizer/            # Current scripts/filter.py
│   └── file-manager/               # Current services/mover, watcher
├── torrent-services/               # All torrent/RSS related services
│   ├── rss-converters/
│   │   ├── eztv-rss-to-json/
│   │   └── subsplease-rss-to-json/
│   ├── magnet-handlers/
│   │   ├── container-magnet/
│   │   ├── transmission-downloader/
│   │   └── platform-launchers/     # windows/linux magnet launchers
│   └── torrent-apis/
│       └── go-eztv-api/
├── web-interfaces/                 # All web UIs and APIs
│   ├── media-viewer/               # Current scripts/main-web.py + app/
│   └── sg-scrape-api/              # If keeping separate from scraper
├── tools/                          # Utilities and maintenance scripts
│   ├── mongo-dedup/
│   ├── useless-remover/
│   └── maintenance-scripts/        # Clear queue, etc.
├── infrastructure/                 # Deployment and ops
│   ├── docker-compose.yml          # Orchestrate related services
│   ├── cloud-init/                 # Current services/create-node
│   └── monitoring/
└── docs/                          # Documentation
    ├── service-dependencies.md     # Which services talk to which
    ├── deployment-guide.md
    └── api-documentation.md
```

### Benefits of This Structure:
1. **Domain separation**: Related services grouped together
2. **Clearer dependencies**: Easier to see what depends on what
3. **Independent deployment**: Each domain can be deployed separately
4. **Technology grouping**: Python services separate from Go services where logical
5. **Documentation**: Clear docs about service relationships
6. **Build simplification**: Each domain can have its own build process

