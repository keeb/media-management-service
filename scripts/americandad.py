import lib.file
import lib.filter

import os
import shutil

"""
We have a problem, that is that the American Dad episodes are
downloading into a folder for each episode.

We want to pull the media out of each folder and then put them in a structured
folder structure likes so

american-dad
-> s1/
--> episodes.mkv


TODO: remove sample shit
"""


class Show:
    def __init__(self, name):
        self.name = name
        self.seasons = []
    
    def add_season(self, season):
        if season == None:
            return
        self.seasons.append(season)

    def exists(self, season):
        for i in self.seasons:
            if i.number() == season: return True
        return False

    def get(self, season):
        for i in self.seasons:
            if i.number() == season: return i
        
        raise Exception("Not Found")       


    def save(self, where):
        """
            saves to a destination `where` in the following format

            show-name
             -> s{season_number}
             --> episodes
        """
        if not lib.file.check_folder(where): os.mkdir(where)
        destination = "%s/american-dad" % where
        os.mkdir(destination)

        # make season folders
        for i in self.seasons:
            season_folder = "%s/s%s" %(destination, i.number())
            print("season_folder is %s" % season_folder)
            if not lib.file.check_folder(season_folder): os.mkdir(season_folder)

            # copy the episodes into the season_folder
            for episode in i.episodes:
                shutil.copy(episode.path(), "%s/" % season_folder)
                


        pass


class Season:
    def __init__(self, number):
        self.season_number = number
        self.episodes = []
    
    def number(self):
        return self.season_number

    def add_episode(self, fpath):
        self.episodes.append(Episode(fpath))

class Episode:
    def __init__(self, fpath):
        self.fpath = fpath

    def path(self):
        return self.fpath
    


def make_struct_from_name(name):
    filename = name.split("/")[-1]
    return {"name": filename, "seeds": 0, "peers": 0}




root_folder = "/mnt/nami/media/video/staging"
files_in_staging = lib.file.crawl_for_files(root_folder)
adad = Show("American Dad")




for file in files_in_staging:
    if "american" in file.lower():
        episode_metadata = lib.filter.parse_show(make_struct_from_name(file), ".")
        
        s = episode_metadata["season"]

        # create the season if it doesn't exist
        if not adad.exists(s): 
            adad.add_season(Season(s))

        # add the episode to the season
        season_object = adad.get(s)
        season_object.add_episode(file)



    
