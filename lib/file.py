import os
import random
import time
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_folder_contents(path): 
    return os.listdir(path)

def crawl_for_files(folder) -> list:
    data = []
    if not check_folder(folder): return []
    for file in os.listdir(folder):
        combined = os.path.join(folder, file)
        if os.path.isdir(combined):
            try:
                for subitem in crawl_for_files(combined):
                    data.append(subitem)
            except:
                print("think we found a dead end.. %s" % combined)
        elif os.path.isfile(combined):
            data.append(combined)
    return data

def crawl_for_folders(folder):
    data = []
    for file in os.listdir(folder):
        combined = os.path.join(folder, file)
        if os.path.isdir(combined):
            data.append(combined)
            for subitem in crawl_for_folders(combined):
                data.append(subitem)
    return data

def get_file_name(file):
    return os.path.basename(file)

def get_random_image(folder):
    photos = []
    for file in get_folder_contents(folder):
        if isphoto(file):
            photos.append(file)
    
    if len(photos) == 0: raise Exception("no photos found")
    return photos[random.randrange(0, len(photos))]

def get_images(folder, max=0):
    images = []
    # don't always want the same photos so lets shuffle the list as
    # we loop through
    contents = get_folder_contents(folder)
    random.shuffle(contents)
    for file in contents:
        if isphoto(file):
            if max == 0:
                images.append(file)
            elif max > 0 and len(images) < max:
                images.append(file)
            else:
                break
    if len(images) == 0: raise Exception("no images found")
    return images

def get_extension(file):
    filename, extension = os.path.splitext(file)
    return extension

def isphoto(file):
    photo_extensions = [".jpg", ".png", ".jpeg", ".gif"]
    if get_extension(file.lower()) in photo_extensions:
        return True
    return False

def ismovie(file):
    movie_extensions = [".mp4", ".mkv", ".mpg", ".mpeg", ".avi", ".flv", ".wmv", \
        ".webm", ".m4v", ".ts"]
    if get_extension(file.lower()) in movie_extensions:
        return True
    return False

def isaudio(file):
    audio_extensions = [".mp3", ".flac", ".ogg"]
    if get_extension(file.lower()) in audio_extensions:
        return True
    return False

def issubtitle(file):
    sub_extensions = [".srt", ".sub", ".smi"]
    if get_extension(file.lower()) in sub_extensions:
        return True
    return False  

def isarchive(file):
    archive_extensions = [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".cbz"]
    if get_extension(file.lower()) in archive_extensions:
        return True
    return False

def isimage(file):
    image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    if get_extension(file.lower()) in image_extensions:
        return True
    return False

def isiso(file):
    iso_extensions = [".iso", ".avhdx", ".vhdx", ".img", ".rar"]
    if get_extension(file.lower()) in iso_extensions:
        return True
    return False      

def ismedia(file):
    if ismovie(file): return True
    if issubtitle(file): return True
    if isphoto(file): return True
    if isaudio(file): return True
    if isiso(file): return True
    return False

def check_folder(path: str) -> bool:
    """Check if folder exists."""
    return os.path.exists(path) and os.path.isdir(path)

def safe_delete_file(path: str) -> bool:
    """Safely delete a single file.
    
    Args:
        path: Path to file to delete
        
    Returns:
        bool: True if file was deleted, False if error
    """
    try:
        if os.path.exists(path) and os.path.isfile(path):
            os.chmod(path, 0o666)  # Make file writable
            os.remove(path)
            return True
    except Exception as e:
        logger.error(f"Error deleting file {path}: {e}")
    return False

def safe_delete_directory(path: str) -> bool:
    """Safely delete a directory and all its contents.
    
    Args:
        path: Path to directory to delete
        
    Returns:
        bool: True if directory was deleted, False if error
    """
    try:
        if not os.path.exists(path) or not os.path.isdir(path):
            return True  # Already gone
            
        # First list all contents
        print(f"Removing directory: {path}")
        contents = os.listdir(path)
        if contents:
            print("Directory contents:")
            for item in contents:
                print(f"  {item}")
        
        # Delete all files first
        for item in contents:
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                if not safe_delete_file(item_path):
                    return False
            elif os.path.isdir(item_path):
                if not safe_delete_directory(item_path):
                    return False
        
        # Verify directory is empty
        remaining = os.listdir(path)
        if remaining:
            print(f"Error: Directory not empty after deletion: {remaining}")
            return False
            
        # Remove the empty directory
        os.rmdir(path)
        return True
        
    except Exception as e:
        print(f"Error deleting directory {path}: {e}")
        return False

def safe_move_file(source: str, dest: str) -> bool:
    """Safely move a file, creating destination directory if needed.
    
    Args:
        source: Source file path
        dest: Destination file path
        
    Returns:
        bool: True if move successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(source, dest)
        return True
    except Exception as e:
        logger.error(f"Error moving file {source}: {e}")
        return False
