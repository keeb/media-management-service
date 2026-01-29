# Go Services

This directory contains Go-based services for the media management system.

## Building

Each service is a standalone Go module with its own `go.mod` file.

```bash
# Build subsplease-rss
cd subsplease-rss
go build -o subsplease-rss-to-json

# Run
./subsplease-rss-to-json
```

## Services

### subsplease-rss

Converts SubsPlease RSS feeds to JSON format for downstream processing.
