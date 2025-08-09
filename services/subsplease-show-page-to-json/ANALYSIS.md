# SubsPlease Show Page to JSON - Service Analysis

## Overview
Intelligent anime episode downloader that queries SubsPlease API and avoids re-downloading existing episodes through smart local filesystem scanning.

## Core Functionality

### Search & Filtering Pipeline
- **`search(query)`**: Queries SubsPlease API, filters out batch downloads (episodes with "##-##" patterns)
- **`filter_results(json, "1080")`**: Extracts 1080p magnet links, maps episode numbers to magnets
- **`filter_range(filtered, start, stop)`**: Supports downloading specific episode ranges
- **`filter_exists(filtered, dirs, show_name)`**: Smart duplicate detection via local directory crawling

### Local Media Intelligence
- Scans hardcoded paths: `/home/keeb/media/video/anime` and `/home/keeb/media/video/staging`
- Uses regex pattern `" {episode_number}[ .[(]"` to identify existing episodes
- Normalizes show names (removes special chars) for accurate matching
- Provides detailed logging of existing vs missing episodes

### Download Integration
- Posts magnet links to `http://hancock:9200/magnet` (custom torrent service)
- Interactive user confirmation before downloading
- Batch processing of multiple episodes

## Technical Dependencies

### External APIs & Services
- **SubsPlease API**: `https://subsplease.org/api/?f=search&tz=America/Los_Angeles&s={query}`
- **Local torrent service**: `hancock:9200/magnet` endpoint
- **File system**: Hardcoded anime directory paths

### Internal Dependencies
- `lib.file.crawl_for_files()`: Recursive directory scanning
- `lib.file.get_file_name()`: Basename extraction

## Data Flow
```
User Input (show name) 
    ↓
SubsPlease API Search 
    ↓
JSON Response Filtering (remove batches, extract 1080p)
    ↓
Local Directory Scanning (anime + staging dirs)
    ↓
Episode Existence Matching (regex + normalization)
    ↓
Missing Episodes List
    ↓
User Confirmation 
    ↓
POST magnets to hancock:9200/magnet
```

## Usage Examples

### Basic Usage
```bash
python show-1080p-magnet.py "chainsaw man"
```

### Episode Range
```bash
python show-1080p-magnet.py "chainsaw man" "5-10"
```

### API Response Structure
```json
{
  "Show Name - 12": {
    "show": "Show Name",
    "episode": "12", 
    "downloads": [
      {"res": "1080", "magnet": "magnet:?..."}
    ]
  }
}
```

## Key Design Patterns

### Intelligent Filtering
- Batch detection prevents downloading entire seasons accidentally
- Resolution filtering focuses on 1080p quality
- Name normalization handles show title variations

### Local State Awareness
- Two-directory scanning catches files in different processing states
- Episode number zero-padding ensures proper matching
- Fuzzy show name matching via normalization

### Safe Download Workflow
- Always previews what will be downloaded
- User confirmation prevents accidental large downloads
- Graceful exit when no new episodes found

## Current Issues & Limitations

### Hardcoded Configuration
- File paths are hardcoded: `/home/keeb/media/video/anime`, `/home/keeb/media/video/staging`
- Torrent service endpoint hardcoded: `http://hancock:9200/magnet`
- Timezone hardcoded: `America/Los_Angeles`

### Error Handling
- Limited error handling for API failures
- No retry logic for network issues
- Basic exception handling with generic messages

### Scalability
- Sequential processing (no concurrent downloads)
- No caching of API responses
- Re-scans entire directory tree each run

### User Experience
- CLI-only interface
- No configuration file support
- Manual episode range specification only

## Integration Points
- **Upstream**: SubsPlease public API
- **Downstream**: Custom torrent service at `hancock:9200`
- **Filesystem**: Local anime media directories
- **Libraries**: Core `lib/file.py` utilities

## Potential Improvements
1. **Configuration management**: Move hardcoded values to config file
2. **Error resilience**: Add retry logic and better error handling
3. **Performance**: Add caching and concurrent processing
4. **Flexibility**: Support multiple quality options, custom directories
5. **Monitoring**: Add logging and download tracking
6. **Integration**: Better integration with other monorepo services