"""
removes useless files in subdir
"""

from lib.file import crawl_for_files, ismedia
import os

root_folder = "/mnt/nami/media/video/movies"

files = crawl_for_files(root_folder)

files_to_remove = []

for file in files:
    if not ismedia(file):
        print("found a shitty file, %s" % file)

        files_to_remove.append(file)


# prompt user to remove files

if len(files_to_remove) == 0:
    print("no files to remove")
    exit()

print("Do you want to remove these files? [y/n]")
print(files_to_remove)
answer = input()
if answer != "y":
    print("exiting")
    exit()

for file in files_to_remove:
    os.remove(file)
    print("removed %s" % file)
