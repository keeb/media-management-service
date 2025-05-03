import os
import re

nums = [x for x in range(0, 100)] # global for now ;/

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
    except:
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

def parse_season_episode(part):
    season = part[1:3]
    episode = part[4:6]
    return (season, episode)


def parse_show_name(show_name):
    # handle the case where release team is before show name

    if show_name.startswith("["):
        return " ".join(show_name.split("]")[1:]).lstrip().replace("-","").rstrip()

    return show_name # just return it if not


def parse(show_name):
    """attempt to figure out if we parse using anime conventions or other scene conventions"""
    show = parse_non_anime(show_name)
    if show.get("season") is None:
        show = parse_anime(show_name)

    return show

def parse_non_anime(show_name):

    """
        Assumptions we're making about the format of show names

        Everything up until SXXEXX is the show name
        SXXEXX is the season and episode
        Everything after SXXEXX until Resolution is the episode name
        Resulution is always a single word: 1080p, 720p
        Resolution is followed by Source - HDTV, WEB-DL
        Source is followed by Encoding as a prefix, release team as suffix
    """

    index = 0
    full_season = False
    encoding = None
    team = None
    resolution = None
    checksum = None
    season = None
    episode = None

    parts = show_name.split(" ")


    for part in parts:

        if part.startswith('[') and part.endswith(']'):
            if not team: # we are going to assume that the first time we find this its always the team and never the checksum
                team = part[1:-1]
            else:
                checksum = part[1:-1]


        if is_season_episode_string(part):
            show_name = parse_show_name(" ".join(parts[:index]))
            season, episode = parse_season_episode(part)
            if episode is None or episode == '':
                full_season = True

        if is_resolution(part):
            resolution = part
        
        if is_encoding(part):
            try:
                encoding, team = part.split("-")
            except:
                pass

        index += 1

    show_info = {"name": show_name,
            "season": season,
            "episode": episode,
            "episode_name": "", # not implemented, todo later probably maybe
            "encoding": encoding,
            "release_team": team,
            "resolution": resolution,
            "full_season": full_season,
            "checksum": checksum
            }
    return show_info



