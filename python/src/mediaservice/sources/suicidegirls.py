"""
SuicideGirls-related data structures and parsing utilities.

Contains:
- Payload: Handles SG job payloads from MongoDB queue
- Album, Model, Models, Photo: Data models for organizing SG content
- Azhdar: Parser for SG torrents uploaded by the uploader 'Azhdar'
"""

import os
import random

from mediaservice.util.file import get_folder_contents


class Payload:
    """
    Handles conversion of a payload and provides helper methods.

    Expected payload format:
    {
        "images": ["https://...jpg", ...],
        "album": "Album Name",
        "model": "Model Name",
        "socials": ["https://instagram.com/...", ...]
    }
    """
    def __init__(self, payload):
        self._payload_dict = payload
        self.unique_id = None
        self.model = None
        self.album = None
        self.socials = None
        self.images = None
        try:
            self._parse(payload)
        except:
            raise Exception("ur payload sux")

    def _parse(self, payload):
        try:
            self.unique_id = payload.get("_id")
        except:
            # not from mongodb
            pass

        model_name = payload.get("model")
        album_name = payload.get("album")
        image_list = payload.get("images")
        socials_list = payload.get("socials")

        self.model = self._sanitize(model_name)
        self.album = self._sanitize(album_name)
        self.images = image_list
        self.socials = socials_list

    def dict(self):
        if self.mongo():
            del self._payload_dict["_id"]
        return self._payload_dict

    def _sanitize(self, name):
        name = name.replace(" ", "-")
        name = name.replace("(", "")
        name = name.replace(")", "")
        name = name.replace(",", "")
        name = name.replace("?", "")
        name = name.replace("&", "and")
        name = name.lower()
        return name

    def __repr__(self):
        return "%s - %s [%s][%s]" % (self.model, self.album, len(self.socials), len(self.images))

    def mongo(self):
        """
        Was this initialized from mongo or can it be found in mongo?
        """
        if self.unique_id == None or self._payload_dict.get("_id") == None:
            return False
        return True


class Photo:
    def __init__(self, path):
        self.path = path

    def _load(self):
        pass

    def __repr__(self):
        return self.path


class Album:
    def __init__(self, name):
        """
        name: the name of the album
        """
        self.name = name
        self._photos = []

    def add_photo(self, photo):
        self._photos.append(photo)

    def random(self):
        photo_amount = len(self._photos)
        if photo_amount == 0 or None:
            raise Exception("no photos in album")

        photo_num = random.randrange(photo_amount)
        return self._photos[photo_num]

    def photos(self):
        return self._photos

    def __repr__(self):
       return self.name


class Model:
    """
    Represents a SuicideGirls model.

    Could be extended with:
     - auto bio information from sg profile
     - link tree generation
    """
    def __init__(self, name):
        self.name = name
        self._albums = []

    def add_album(self, album):
        self._albums.append(album)

    def albums(self):
        return self._albums

    def __repr__(self):
        return self.name


class Models:
    """
    A collection of Model objects and operations around them.
    """
    def __init__(self):
        self.models = []

    def find_model_by_name(self, name):
        """
        Finds a model in model list or returns a new model.
        """
        for m in self.models:
            if m.name == name:
                return m
        return Model(name)

    def add_model(self, model):
        self.models.append(model)

    def __repr__(self):
        return str([x.name for x in self.models])

    def __len__(self):
        return len(self.models)

    def __getitem__(self, val):
        return self.models[val]


class Azhdar:
    """
    Parser for SuicideGirls content uploaded by 'Azhdar' on x1337x.ws.

    All uploads follow a similar format:
    "ModelName Photo Album_ album name _ SuicideGirls"
    """
    def __init__(self, root):
        self.root_folder = root
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
            album_folder = os.path.join(self.root_folder, folder)
            model_name = self._extract_model_name(folder)

            sg_model = self._models.find_model_by_name(model_name)
            album_name = self._extract_album_name(folder)

            new_album = Album(album_name)
            for photo_name in get_folder_contents(album_folder):
                photo_path = os.path.join(album_folder, photo_name)
                photo = Photo(photo_path)
                new_album.add_photo(photo)

            sg_model.add_album(new_album)
            self._models.add_model(sg_model)

    def _extract_album_name(self, folder):
        """
        Example: "Sophoulla Photo Album_ old money _ SuicideGirls"
        Returns: "old money"
        """
        dirty = folder.split("_ ")[1]
        return dirty

    def _extract_model_name(self, folder):
        """
        Example: "Sophoulla Photo Album_ old money _ SuicideGirls"
        Returns: "Sophoulla"
        """
        dirty = folder.split("Photo Album")[0].rstrip()
        return dirty
