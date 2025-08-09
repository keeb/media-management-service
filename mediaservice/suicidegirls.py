import os
import random

from lib.file import get_folder_contents
from model import Album, Model, Models, Photo



class Azhdar:
    """
        A popular SuicideGirls image uploader on https://x1337x.ws
        All uploads follow a similar format and thus this is the way we extract info from the files

    """
    def __init__(self, root):
        self.root_folder = root
        
        # need empty models to fill
        # need empty albums to fill
        self._models = Models()

        self.load()


    def load(self):
        self._initialize()


    def get_random_model(self):
        total_models = len(self._models)
        if total_models == 0 or None:
            raise Exception("Models were not initialized correctly")
        
        random_model_num = random.randrange(total_models)
        return self._models[random_model_num]
    
    def get_model(self, name):
        return self._models.find_model_by_name(name)
    

    def models(self):
        return self._models


    def _initialize(self):
        for folder in get_folder_contents(self.root_folder):
            # extract the info here
            album_folder = os.path.join(self.root_folder, folder)
            model_name = self._extract_model_name(folder)

            # start to create new model information it does not exist
            sg_model = self._models.find_model_by_name(model_name)
            album_name = self._extract_album_name(folder)

            new_album = Album(album_name)
            # lets find the Photos and add them into the album
            for photo_name in get_folder_contents(album_folder):
                photo_path = os.path.join(album_folder, photo_name)
                photo = Photo(photo_path)
                new_album.add_photo(photo)

            # finally add the album to the model
            sg_model.add_album(new_album)
            self._models.add_model(sg_model)
        
        
    def _extract_album_name(self, folder):
        """
            example: Sophoulla Photo Album_ old money _ SuicideGirls
            returns Old Money
            
            do this by splitting by _ and getting the 2nd element.
        """

        dirty = folder.split("_ ")[1]
        return dirty

        
    def _extract_model_name(self, folder):
        """
            example: Sophoulla Photo Album_ old money _ SuicideGirls

            returns Sophoulla
        """
        dirty = folder.split("Photo Album")[0].rstrip()
        return dirty