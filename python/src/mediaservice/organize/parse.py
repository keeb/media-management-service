import os
import re

# Common helper functions
def is_resolution(part: str) -> bool:
    """Check if string contains resolution marker."""
    resolutions = ["1080p", "720p", "480p", "2160p", "4k", "uhd"]
    # Remove brackets if present
    clean_part = part.strip("[]()").lower()
    return any(res.lower() in clean_part for res in resolutions)

def is_year(part: str) -> bool:
    """Check if string contains a year between 1900-2099."""
    try:
        # Remove brackets/parens and extract digits
        clean_part = part.strip("[]()").lower()
        year = int(''.join(c for c in clean_part if c.isdigit())[:4])
        return 1900 <= year <= 2099
    except (ValueError, IndexError):
        return False

def is_encoding(part: str) -> bool:
    """Check if string contains encoding information."""
    encodings = ["h264", "x264", "x265", "h265", "aac2", "xvid"]
    return any(encoding in part.lower() for encoding in encodings)

# TV Show Detection and Parsing
def is_season_episode_string(part: str) -> bool:
    """Check if string contains season/episode marker."""
    # Convert dots to spaces for consistent parsing
    part = part.replace('.', ' ')
    # Common patterns: S01E01, 1x01, etc
    patterns = [
        r'S\d{1,2}E\d{1,2}',  # S01E01
        r'\d{1,2}x\d{1,2}',   # 1x01
        r'E\d{1,2}'           # E01 (episode only)
    ]
    return any(re.search(pattern, part, re.IGNORECASE) for pattern in patterns)

def is_tv(filename: str) -> bool:
    """Check if filename matches TV show patterns."""
    # Split by extension first
    filename = os.path.splitext(filename)[0]
    
    # Convert dots to spaces for consistent parsing
    parts = filename.replace('.', ' ').split()
    
    # Must have season/episode marker
    if not any(is_season_episode_string(part) for part in parts):
        return False
        
    return True

def parse_tv(filename: str) -> dict:
    """Parse TV show information from filename."""
    tv_info = {
        "name": "",
        "season": "",
        "episode": "",
        "resolution": "",
        "encoding": "",
        "release_team": ""
    }
    
    # Split by extension first
    filename = os.path.splitext(filename)[0]
    
    # Convert dots to spaces for consistent parsing
    parts = filename.replace('.', ' ').split()
    
    # Find the season/episode marker to split name
    name_parts = []
    found_marker = False
    for part in parts:
        if is_season_episode_string(part):
            found_marker = True
            break
        name_parts.append(part)
    
    if found_marker:
        tv_info["name"] = " ".join(name_parts)
        
    return tv_info

# Anime Detection and Parsing
def is_anime(filename: str) -> bool:
    """Check if filename matches anime patterns."""
    # Anime typically starts with [Team] and has simple episode numbers
    if not (filename.startswith('[') and ']' in filename):
        return False
        
    parts = filename.split(" ")
    has_episode = any(part.isdigit() and len(part) <= 2 for part in parts)
    has_resolution = any(is_resolution(part) for part in parts)
    
    return has_episode and has_resolution

def parse_anime(filename: str) -> dict:
    """Parse anime filename into components."""
    show_info = {
        "name": "",
        "season": None,
        "episode": None,
        "release_team": None,
        "resolution": None,
        "checksum": None
    }
    
    parts = filename.split(" ")
    index = 0
    
    for part in parts:
        if part.startswith('['):
            if not show_info["release_team"]:
                show_info["release_team"] = part[1:-1]
            else:
                if "." in part:
                    c = part.split(".")[0]
                    show_info["checksum"] = c[1:-1]
                else:
                    show_info["checksum"] = part[1:-1]
        
        if part.isdigit():
            show_info["name"] = " ".join(parts[1:index]).strip()
            show_info["episode"] = part
            
        if is_resolution(part):
            show_info["resolution"] = part.strip('()')
            
        index += 1
    
    return show_info

# Movie Detection and Parsing
def is_movie(filename: str) -> bool:
    """Check if filename matches movie patterns."""
    if 'sample' in filename.lower():
        return False
        
    # Handle both period-separated and space-separated formats
    parts = filename.replace('.', ' ').split(' ')
    
    has_year = any(is_year(part) for part in parts)
    has_resolution = any(is_resolution(part) for part in parts)
    
    has_season_episode = any(is_season_episode_string(part) for part in parts)
    has_simple_episode = any(part.isdigit() and len(part) <= 2 for part in parts)
    
    # Add more movie source indicators
    movie_indicators = [
        'extended', 'directors.cut', 'remastered', 'bluray', 'web-dl', 'bdrip',
        'yts', 'rarbg', 'yify', 'remux', 'proper', 'rerip'
    ]
    has_movie_indicator = any(indicator in filename.lower() for indicator in movie_indicators)
    
    return (has_year and 
            has_resolution and 
            not has_season_episode and 
            not has_simple_episode and 
            (has_movie_indicator or has_resolution))

def parse_movie(filename: str) -> dict:
    """Parse movie filename into components."""
    movie_info = {
        "name": "",
        "year": None,
        "resolution": None,
        "encoding": None,
        "release_team": None
    }
    
    parts = filename.replace('.', ' ').split(' ')
    name_parts = []
    found_year = False
    
    for part in parts:
        if not found_year:
            if is_year(part):
                movie_info["year"] = part
                found_year = True
            else:
                name_parts.append(part)
        else:
            if is_resolution(part):
                movie_info["resolution"] = part
            elif is_encoding(part):
                movie_info["encoding"] = part
            elif part.startswith('[') and part.endswith(']'):
                movie_info["release_team"] = part[1:-1]
    
    movie_info["name"] = " ".join(name_parts)
    return movie_info


