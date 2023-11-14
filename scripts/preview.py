#!/usr/bin/env python
import os.path
import shutil

from lib.suicidegirls import Azhdar


if __name__ == "__main__":
    root_folder = "/root"
    output_folder = "/output"

    num_files = 1 # not yet implemented

    a = Azhdar(root_folder)

    for model in a.models():
        for album in model.albums():
            random_photo = album.random()
            old_file_name = os.path.basename(random_photo.path)
            new_file_name = old_file_name.replace(".jpg", "-%s.jpg" %(model.name))
            new_file_path = os.path.join(output_folder, new_file_name)
            
            shutil.copy(random_photo.path, new_file_path)

    

