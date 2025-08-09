# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Service Overview

The cleaner service is a Python utility that manages Transmission BitTorrent client torrents by removing completed ones. It's a single-file service that depends on the shared `transmission` module from the parent project's `lib/` directory.

## Development Commands

### Running the Service

```bash
python cleaner.py
```

The service runs as a standalone script and performs the following operations:
1. Lists current torrents in Transmission
2. Calls `remove_complete_torrents()` method
3. Shows remaining torrents after cleanup

### Dependencies

- Requires the `transmission` module from `../../lib/transmission.py`
- Uses Python 3 standard library (`sys`, `json`)
- Assumes Transmission daemon is running and accessible

## Architecture

This is a simple test/utility service with minimal structure:

- **Single file**: `cleaner.py` - Main execution script
- **External dependency**: `transmission.TransmissionRequest` class from parent project
- **Purpose**: Testing and demonstrating the `remove_complete_torrents()` functionality

The service imports the transmission module by adding the current directory to the Python path, suggesting it expects to be run from a location where the `lib/` directory is accessible.

## Key Functionality

The service demonstrates:
- Listing torrents before cleanup
- Removing completed torrents via Transmission RPC
- Verifying results after cleanup
- Error handling for API responses

This appears to be a test/utility script rather than a production service, as evidenced by the extensive debugging output and test-oriented structure.

## Systemd Integration

The service can be run automatically using systemd:

### Installation

```bash
# Copy unit files to systemd directory
sudo cp ../../units/cleaner.service /etc/systemd/system/
sudo cp ../../units/cleaner.timer /etc/systemd/system/

# Enable and start the timer
sudo systemctl daemon-reload
sudo systemctl enable cleaner.timer
sudo systemctl start cleaner.timer
```

### Management

```bash
# Check timer status
sudo systemctl status cleaner.timer

# Check service status
sudo systemctl status cleaner.service

# View logs
sudo journalctl -u cleaner.service

# Run service manually
sudo systemctl start cleaner.service
```

The timer runs daily at 1:00 AM to automatically clean completed torrents from Transmission.