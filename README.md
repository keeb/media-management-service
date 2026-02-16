# media-management-service

A monorepo for all of the media management projects I have written.

## Python Package

The core library lives in `python/src/mediaservice/` and provides a unified CLI (`mms`) for media automation:

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# CLI
mms worker              # Process and organize downloaded media
mms clean               # Clean up media files
mms index               # Index media files to MongoDB
mms inventory scan      # Scan Jellyfin library inventory + watch activity
mms download subsplease # Download anime from SubsPlease
mms download erai       # Download anime from Erai-raws
mms sg worker           # SuicideGirls download worker
mms sg scrape           # SuicideGirls scraper
```

### Inventory & Monitoring

`mms inventory scan --push-metrics` queries Jellyfin for library counts and watch activity, then pushes metrics to a Prometheus Pushgateway. A Grafana dashboard ("Media Library Inventory") visualizes:

- Library totals (anime/movies/shows titles and episodes)
- Watch activity (episodes watched in last 7d/30d, all-time total)
- Continue watching list with progress percentages

Requires `JELLYFIN_API_KEY` env var (or `--api-key` flag).

## Go Services

- `go/subsplease-rss/` - Converts SubsPlease RSS to JSON

## Legacy Services

21 independent microservices in `services/` (mixed Python/Go/Docker) covering RSS conversion, torrent handling, file management, and platform-specific magnet launchers.

## Systemd Units

Service/timer pairs in `units/` for automated anime downloads.
