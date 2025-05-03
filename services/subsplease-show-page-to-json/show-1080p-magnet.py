import sys
import requests
import json
import lib.file
import re


def search(query):
    if " " in query:
        query = query.replace(" ", "+")

    url = 'https://subsplease.org/api/?f=search&tz=America/Los_Angeles&s=' + query
    print(f"\nSearching: {query}")
    response = requests.get(url)
    result = response.json()
    
    # Filter out batch entries if result is a dict
    if isinstance(result, dict):
        filtered_result = {}
        for key, value in result.items():
            # Skip if key contains episode range pattern (##-##)
            if not re.search(r'\d{2}-\d{2}', key):
                filtered_result[key] = value
        result = filtered_result
    
    return result

def filter_results(json, term):
    filtered = {}
    if isinstance(json, list):
        print("No results found")
        return filtered
    
    for key in json.keys():
        number = key.split(" ")[-1]
        download_info = json.get(key).get("downloads")
        for info in download_info:
            if info.get("res") == term:
                filtered[number] = info.get("magnet")
    
    return filtered

def filter_range(filtered, start, stop):
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

def normalize(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', s.lower())

def filter_exists(filtered: dict, download_dir: str, key_identifier: str = None) -> dict:
    """Remove episodes from the filtered dictionary that appear to already exist."""
    print(f"\nChecking directory: {download_dir}")
    print(f"Show: {key_identifier}")
    
    existing_files = lib.file.crawl_for_files(download_dir)
    print(f"Found {len(existing_files)} existing files")
    
    remaining = {}

    for episode, magnet in filtered.items():
        episode_str = episode.zfill(2)
        exists = False

        for file in existing_files:
            filename = lib.file.get_file_name(file)
            episode_pattern = f" {episode_str}[ .[(]"
            if re.search(episode_pattern, filename):
                if key_identifier:
                    normalized_identifier = normalize(key_identifier)
                    normalized_filename = normalize(filename)
                    if normalized_identifier in normalized_filename:
                        exists = True
                        print(f"Episode {episode_str} exists: {filename}")
                        break
                else:
                    exists = True
                    print(f"Episode {episode_str} exists: {filename}")
                    break

        if not exists:
            print(f"Episode {episode_str} not found")
            remaining[episode] = magnet

    if remaining:
        print(f"\nEpisodes to download: {list(remaining.keys())}")
    else:
        print("\nNo new episodes to download")
    return remaining

def download(filtered_results_list):
    for key in filtered_results_list.keys():
        magnet = filtered_results_list[key]
        print("Downloading " + magnet)

        url = "http://hancock:9200/magnet"
        header = {'Content-type': 'application/json'}
        data = {"magnet": magnet}
        response = requests.post(url, data=json.dumps(data), headers=header)
        print(response.text)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 show-1080p-magnet.py <show name> <amount|all>")
        exit(1)

    term = sys.argv[1]
    print("Searching for " + term)
    results = filter_results(search(term), "1080")

    if len(sys.argv) == 3:
        if "-" in sys.argv[2]:
            start, stop = sys.argv[2].split("-")
            results = filter_range(results, int(start), int(stop))

    if len(results) == 0:
        print("No results found")
        exit(0)
    
    anime_dir = "/home/keeb/media/video/anime"  
    staging_dir = "/home/keeb/media/video/staging"
    dirs_to_check = [anime_dir, staging_dir]
    for dir in dirs_to_check:
        results = filter_exists(results, dir, key_identifier=term)
        
        if len(results) == 0:
            print("All episodes already exist locally")
            exit(0)

    print(f"Found {len(results)} episodes to download")
    input = input("Download? (y/n): ")
    if input == "y":
        download(results)
    else:
        print("Not downloading")
        print(results)
        exit(0)



