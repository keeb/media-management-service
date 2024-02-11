import sys
import requests
import json

def search(query):
    if " " in query:
        query = query.replace(" ", "+")

    url = 'https://subsplease.org/api/?f=search&tz=America/Los_Angeles&s=' + query
    response = requests.get(url)
    return response.json()

def filter_results(json, term):
    filtered = {}
    # need to see if json.keys is empty or has bad type
    if isinstance(json, list):
        return filtered
    
    for key in json.keys():
        number = key.split(" ")[-1]
        download_info  = json.get(key).get("downloads")
        for info in download_info:
            if info.get("res") == term:
                filtered[number] = info.get("magnet")
    
    return filtered

def filter_range(filtered, start, stop):

    """
    always going to be in reverse order so

    Helck - 24
    Helck - 23
    .
    .

    so loop through all the keys and when we hit the stop, set started to true until we hit start.

    So helck 2-3 would be
    02, 03



    """
    wat = {}
    started = False
    for key in filtered.keys():

        if int(key) == stop:
            started = True

        if int(key) + 1 == start:
            break

        if started:
            wat[key] = filtered[key]
    
    return wat


def download(filtered_results_list):
    # assume the url is available
    for key in filtered_results_list.keys():
        magnet = filtered_results_list[key]
        print("Downloading " + magnet)

        # json post to the download service
        url = "http://hancock:9200/magnet"
        header = {'Content-type': 'application/json'}
        data = {"magnet": magnet}
        response = requests.post(url, data=json.dumps(data), headers=header)
        print(response.text)

    

if __name__ == '__main__':

    # check if the user has provided a term
    if len(sys.argv) < 2:
        print("Usage: python3 show-1080p-magnet.py <show name> <amount|all>")
        exit(1)


    term = sys.argv[1]
    print("Searching for " + term)
    results = filter_results(search(term), "1080")

    # default to downloading all
    dlall = True


    # see if a range was provided, i.e. 1-5
    if len(sys.argv) == 3:
        if "-" in sys.argv[2]:
            start, stop = sys.argv[2].split("-")
            results = filter_range(results, int(start), int(stop))

    if len(results) == 0:
        print("No results found")
        exit(0)
    
    print(f"found {len(results)} results")
    input = input("Download? (y/n): ")
    if input == "y":
        download(results)
    else:
        print("Not downloading")
        print(results)
        exit(0)



