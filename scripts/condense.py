#!/usr/bin/env python3

"""
take a folder, with subfolders, remove the shit from subfolders, and move the movies to the top level
"""
from lib.file import get_folder_contents, crawl_for_files, ismovie
import shutil
import os

root_folder = "/mnt/nami/media/video/movies"
files = get_folder_contents(root_folder)

shitty_files = []

for item in files:
    fpath = f"{root_folder}/{item}"
    if os.path.isdir(fpath):
        subdir_files = crawl_for_files(fpath)
        if len(subdir_files) == 0:
            try:
                os.rmdir(fpath)
            except: 
                print(f"couldnt remove, do it manually, {fpath}")
        for sub_file in subdir_files:
            if not ismovie(sub_file):
                shitty_files.append(sub_file)
            else:
                shutil.move(sub_file, root_folder)
                


if len(shitty_files) > 0:
    print("found shitty files")
    for i in shitty_files:
        print(i)

answer = input()
if answer != "y":
    print("exiting")
    exit()

for i in shitty_files:
    os.remove(i)