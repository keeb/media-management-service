import json

nums = [x for x in range(0, 100)] # global for now ;/

def is_on_watchlist(name):
    watchlist = ["Doctors"]

    if name in watchlist:
        return True

def choose(list_of_same_show):
    """
        Rules are:

        1. Highest quality wins
        2. Team preference
        3. Maybe we worry about encoding?
        4. Seeds
    """



def is_season_episode_string(part):
    if part.startswith("S"):
        for i in nums:
            if str(i) in part:
                return True

def is_resolution(part):
    resolutions = ["1080p", "720p", "480p", "2160p"]
    if part in resolutions:
        return True

def is_encoding(part):
    encodings = [ \
        "h264", "x264", "x265", "h265", "aac2",  \
        "xvid", \
        ]
    lower = part.lower()
    for encoding in encodings:
        if encoding in lower:
            return True
    
    return False


def parse_season_episode(part):
    season = part[1:3]
    episode = part[4:6]
    return (season, episode)

def parse_show(show):

    """
        Assumptions we're making about the format of show names

        Everything up until SXXEXX is the show name
        SXXEXX is the season and episode
        Everything after SXXEXX until Resolution is the episode name
        Resulution is always a single word: 1080p, 720p
        Resolution is followed by Source - HDTV, WEB-DL
        Source is followed by Encoding as a prefix, release team as suffix
    """

    show_name = show["name"]
    split_name = show_name.split(" ")
    index = 0
    full_season = False
    encoding = None
    team = None
    resolution = None


    for part in split_name:

        if is_season_episode_string(part):
            show_name = " ".join(split_name[:index])
            season, episode = parse_season_episode(part)
            if episode is None or episode == '':
                full_season = True

        if is_resolution(part):
            resolution = split_name[index]
        
        if is_encoding(part):
            try:
                encoding, team = part.split("-")
            except:
                pass
        
        index += 1

    show_info = {"name": show_name,
            "season": season,
            "episode": episode,
            "episode_name": "", # not implemented, todo later probably maybe
            "encoding": encoding,
            "seeds": show["seeds"],
            "peers": show["peers"],
            "release_team": team,
            "resolution": resolution,
            "full_season": full_season
            }

    # print(json.dumps(show_info, indent=2)) # debug
    return show_info

# with open("result.json") as f:
#     data = json.load(f)
#     f.close()

# for show in data["show"]:
#     show_info = parse_show(show)
#     if is_on_watchlist(show_info["name"]):
#         print(json.dumps(show_info, indent=2))


show = {
    "name": "The Handmaids Tale S05E10 Safe 1080p HULU WEBRip DD5 1 X 264-EVO [eztv]",
    "seeds": 0,
    "peers": 0,
}

print(json.dumps(parse_show(show), indent=2))
