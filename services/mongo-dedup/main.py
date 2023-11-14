from pymongo import MongoClient

client = MongoClient("mongodb://treehouse:mongo@localhost:27017")
db = client.mm
collection = db.new 
records = collection.find({}, limit=0, allow_disk_use=True)
        

class Record:
    def __init__(self, _id, updated, shows):
        self._id = id
        self.updated = updated
        self.shows = shows


class Collection:
    def __init__(self):
        self.show_list = []

    def exists(self, filename):
        for show in self.show_list:   
            if show.get("filename") == filename:
                return True
        return False
    
    def add(self, show):
        self.show_list.append(show)

    def save(self):
        db.tmp.insert_one(self.show_list)


"""
a collection is a list of all deduped `shows`

each record contains a list of `shows`

match record against collection



"""

c = Collection()
for item in records:
    _id = item.get("_id") # ultimate will delete by id..
    updated = item.get("updated")
    show_list = item.get("show")
    for show in show_list:
        fname = show.get("filename")
        if not c.exists(fname):
            c.add(show)

c.save()