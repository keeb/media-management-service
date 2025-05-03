import os
import shutil
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from lib.file import (
    check_folder, get_folder_contents, ismedia, 
    safe_move_file, safe_delete_directory
)
from lib.parse import is_anime, is_tv, parse_anime, parse_tv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def sanitize_path(path: str) -> str:
    """Convert path string to clean, absolute path.
    
    Args:
        path: Raw path string that may contain relative paths or symlinks
        
    Returns:
        str: Absolute, normalized path with symlinks resolved
    """
    return str(Path(path).resolve())

# Base directory configuration
STAGING_DIR = sanitize_path("/home/keeb/media/video/staging")
ANIME_DIR = sanitize_path("/home/keeb/media/video/anime/completed")
MOVIES_DIR = sanitize_path("/home/keeb/media/video/movies")
TV_DIR = sanitize_path("/home/keeb/media/video/shows")

def normalize_show_name(name: str) -> str:
    """Normalize show name for directory structure.
    
    Args:
        name: Raw show name
        
    Returns:
        str: Normalized name (lowercase, hyphens, no trailing separators)
    """
    # Convert to lowercase
    name = name.lower()
    # Remove any trailing separators
    name = name.strip(' -_.')
    # Replace spaces with hyphens
    name = name.replace(' ', '-')
    # Remove any duplicate hyphens
    while '--' in name:
        name = name.replace('--', '-')
    # Remove any remaining trailing hyphens
    return name.strip('-')

def process_media_files(preview: bool = True) -> None:
    """Process media files from staging directory.
    
    Handles three types of media:
    1. Anime files (loose files with [Team] prefix)
    2. TV shows (not implemented yet)
    3. Movies (in directories)
    
    Args:
        preview: If True, shows planned operations without executing
        
    Returns:
        None
    """
    if not check_folder(STAGING_DIR):
        logger.error(f"Staging directory {STAGING_DIR} not found")
        return

    moves: List[Tuple[str, str]] = []  # (source_path, dest_path)
    deletes: List[str] = []  # paths to delete
    
    # Handle loose files (anime and TV)
    for filename in get_folder_contents(STAGING_DIR):
        source_path = sanitize_path(os.path.join(STAGING_DIR, filename))
        if os.path.isdir(source_path):
            continue
            
        # Try anime first
        if is_anime(filename):
            anime_info = parse_anime(filename)
            if anime_info["name"]:
                show_name = normalize_show_name(anime_info["name"])
                if ismedia(filename):
                    dest_dir = sanitize_path(os.path.join(ANIME_DIR, show_name))
                    dest_path = os.path.join(dest_dir, filename)
                    moves.append((source_path, dest_path))
            continue

        # Try TV show
        if is_tv(filename):
            tv_info = parse_tv(filename)
            if tv_info["name"]:
                show_name = normalize_show_name(tv_info["name"])
                if ismedia(filename):
                    dest_dir = sanitize_path(os.path.join(TV_DIR, show_name))
                    dest_path = os.path.join(dest_dir, filename)
                    moves.append((source_path, dest_path))
            continue
    
    # Then handle directories (typically movies)
    for dirname in get_folder_contents(STAGING_DIR):
        dir_path = sanitize_path(os.path.join(STAGING_DIR, dirname))
        if not os.path.isdir(dir_path):
            continue
            
        # Find video files in the directory
        media_files = [f for f in os.listdir(dir_path) 
                      if ismedia(f) and 'sample' not in f.lower()]
        
        if not media_files:
            deletes.append(dir_path)
            continue
            
        # Move the first video file found
        main_video = media_files[0]
        source_path = sanitize_path(os.path.join(dir_path, main_video))
        dest_path = sanitize_path(os.path.join(MOVIES_DIR, main_video))
        moves.append((source_path, dest_path))
        deletes.append(dir_path)

    if not moves and not deletes:
        logger.info("No files to process")
        return

    # Preview mode
    if preview:
        if moves:
            print("\nPlanned moves:")
            for source, dest in moves:
                print(f"  MOVE: {os.path.basename(source)} -> {os.path.dirname(dest)}")
        
        if deletes:
            print("\nPlanned deletions:")
            for delete in deletes:
                print(f"  DELETE: {delete}")
        
        response = input("\nProceed with these operations? (y/N): ").lower()
        if response != 'y':
            logger.info("Operation cancelled by user")
            return

    # Execute operations
    # First do all the moves
    for source, dest in moves:
        if safe_move_file(source, dest):
            logger.info(f"Moved {os.path.basename(source)} to {os.path.dirname(dest)}")
        else:
            logger.error(f"Failed to move {source}")
    
    # Then handle all the deletes
    for delete in deletes:
        if safe_delete_directory(delete):
            logger.info(f"Deleted {delete}")
        else:
            logger.error(f"Failed to delete {delete}")

def main() -> None:
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process media files from staging directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s             # Run in preview mode
  %(prog)s --execute   # Execute moves and deletions
        """
    )
    parser.add_argument('--execute', '-e', action='store_true', 
                       help='Execute operations without preview')
    
    args = parser.parse_args()
    
    process_media_files(preview=not args.execute)

if __name__ == "__main__":
    main()
