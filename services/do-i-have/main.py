from services.parser.filter import parse
from lib.file import crawl_for_files, get_file_name

"""
base_path = "/mnt/nami/media/video/"

folders_to_check = [
    base_path + "staging",
    base_path + "anime/completed",
]
"""


folders_to_check = [
        "/mnt/nami/media/video/anime/completed/tasuuketsu/"
]


file_to_check = "[SubsPlease] Tasuuketsu - 03 (1080p) [BA14A9B4].mkv"
parsed_file = parse(file_to_check)
show_name = parsed_file.get("name")
episode = parsed_file.get("episode")


for folder in folders_to_check:
    content = crawl_for_files(folder)
    for file in content:
        file_name = get_file_name(file)
        parsed = parse(file_name)
        if show_name == parsed.get("name") and episode == parsed.get("episode"):
            print("Found %s" % file_name)
            break
