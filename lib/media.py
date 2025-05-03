import os
from lib.parse import parse_movie, is_year

def get_anime_info(filename: str) -> tuple[bool, str]:
    """Determine if a file is anime and extract show name for organization.
    
    Args:
        filename: The filename to analyze
        
    Returns:
        tuple[bool, str]: (is_anime, show_name)
        - is_anime: True if file appears to be anime
        - show_name: Normalized show name (lowercase with hyphens) if is_anime, else empty string
    """
    # Split by extension first
    filename = os.path.splitext(filename)[0]
    
    # Check if starts with [Team]
    if not (filename.startswith("[") and "]" in filename):
        return False, ""
    
    try:
        # Split into parts
        team = filename[1:filename.index("]")]
        remaining = filename[filename.index("]")+1:].strip()
        
        # Split by " - "
        parts = remaining.split(" - ")
        if len(parts) < 2:
            return False, ""
            
        show_name = parts[0].strip()
        episode_part = parts[1].split(" ")[0]  # Take first part in case of (1080p) etc.
        
        # Check if we have what looks like an episode number or OVA
        cleaned_ep = episode_part.replace("v2", "").replace("v3", "")
        if cleaned_ep.isdigit() or cleaned_ep == "OVA":
            show_name = show_name.lower().replace(" ", "-")
            return True, show_name
            
    except Exception as e:
        print(f"Error parsing: {e}")
        return False, ""
    
    return False, ""

def get_movie_info(filename: str) -> tuple[bool, str]:
    """Determine if a file is a movie and extract movie name for organization.
    
    Args:
        filename: The filename to analyze
        
    Returns:
        tuple[bool, str]: (is_movie, movie_name)
        - is_movie: True if file appears to be a movie
        - movie_name: Normalized movie name if is_movie, else empty string
    """
    # Skip obvious non-movies
    if filename.startswith('[SubsPlease]') or 'sample' in filename.lower():
        return False, ""
        
    # Only consider video files
    if not any(filename.lower().endswith(ext) for ext in ['.mp4', '.mkv', '.avi']):
        return False, ""
    
    # Parse the filename
    base_name = os.path.splitext(filename)[0]
    movie_info = parse_movie(base_name)
    
    # Criteria for a movie:
    # 1. Must have a name
    # 2. Must have a year (to distinguish from TV episodes)
    # 3. Should typically have a resolution
    if (movie_info["name"] and 
        movie_info["year"] and 
        movie_info["resolution"]):
        
        return True, movie_info["name"].lower()
    
    return False, "" 