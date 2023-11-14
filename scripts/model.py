import random

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
        think about adding 
         - auto bio information from sg profile
         - link tree generation 
    """
    def __init__(self, name):
        self.name = name

        # do we have any albums associated with the Model?
        self._albums = []
    

    def add_album(self, album):
        self._albums.append(album)
    
    def albums(self):
        return self._albums

    def __repr__(self):
        return self.name


class Models:
    """
    a collection of `Model` and operations around them
    """
    def __init__(self):
        self.models = []


    def find_model_by_name(self, name):
        """ 
            finds a model in model list or returns a new model
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



class Photo:
    def __init__(self, path):
        self.path = path

    def _load(self):
        pass

    def __repr__(self):
        return self.path
    
