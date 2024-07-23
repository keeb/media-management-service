"""
removes useless files in subdir
"""

from lib.file import crawl_for_files, ismedia, isarchive, isphoto
import os
import argparse

root_folder = "/mnt/nami/media/video/"

argparser = argparse.ArgumentParser(description="removes useless files in subdir")
argparser.add_argument("--root_folder", help="root folder to start from", default=root_folder)
argparser.add_argument("--dry-run", help="don't actually remove files", action="store_true")
argparser.add_argument("--verbose", help="show more output", action="store_true")
argparser.add_argument("--filter", help="filter files by extension", default="")
args = argparser.parse_args()

if args.root_folder:
    print("have a root folder) %s" % args.root_folder)

files = crawl_for_files(root_folder)
files_to_remove = []

if args.filter:
    print ("have filter %s" % args)
    files_to_remove = [file for file in files if file.endswith(args.filter)]

else:
    for file in files:
        if not ismedia(file) and not isarchive(file) and not isphoto(file):
            files_to_remove.append(file)

if len(files_to_remove) == 0:
    print("no files to remove")
    exit()

if args.dry_run:
    print("number of files to remove: %d" % len(files_to_remove))
    if args.verbose:
        print(files_to_remove)
    exit()

for file in files_to_remove:
    os.remove(file)
    print("removed %s" % file)
