import os
import random

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

def check_folder(folder):
    try:
        os.listdir(folder)
        return True
    except:
        return False
