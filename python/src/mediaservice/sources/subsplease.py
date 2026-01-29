"""
SubsPlease anime episode search and download utilities.
"""

import re
import json
import requests

from mediaservice.util.file import crawl_for_files, get_file_name


def search(query: str) -> dict:
    """Search SubsPlease API for anime episodes.

    Args:
        query: Show name to search for

    Returns:
        Dictionary of episode results
    """
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


def filter_results(results: dict, resolution: str = "1080") -> dict:
    """Filter search results to only include specified resolution.

    Args:
        results: Raw search results from SubsPlease API
        resolution: Resolution to filter for (e.g. "1080", "720")

    Returns:
        Dictionary mapping episode number to magnet link
    """
    filtered = {}
    if isinstance(results, list):
        print("No results found")
        return filtered

    for key in results.keys():
        # For movies, use the full title (excluding " - Movie") as the identifier
        if key.endswith(" - Movie"):
            parts = key.rsplit(" - Movie", 1)[0].split(" - ", 1)
            number = parts[1] if len(parts) > 1 else parts[0]
        else:
            number = key.split(" ")[-1]

        download_info = results.get(key).get("downloads")
        for info in download_info:
            if info.get("res") == resolution:
                filtered[number] = info.get("magnet")

    return filtered


def filter_range(filtered: dict, start: int, stop: int) -> dict:
    """Filter results to only include episodes within a range.

    Args:
        filtered: Dictionary of episode -> magnet
        start: Start episode number
        stop: Stop episode number

    Returns:
        Filtered dictionary
    """
    result = {}
    started = False
    for key in filtered.keys():
        if int(key) == stop:
            started = True

        if int(key) + 1 == start:
            break

        if started:
            result[key] = filtered[key]

    return result


def normalize(s: str) -> str:
    """Normalize string for comparison."""
    return re.sub(r'[^a-z0-9]', '', s.lower())


def filter_exists(filtered: dict, download_dir: str, key_identifier: str = None) -> dict:
    """Remove episodes from results that already exist in directory.

    Args:
        filtered: Dictionary of episode -> magnet
        download_dir: Directory to check for existing files
        key_identifier: Show name to match against filenames

    Returns:
        Dictionary with existing episodes removed
    """
    print(f"\nChecking directory: {download_dir}")
    print(f"Show: {key_identifier}")

    existing_files = crawl_for_files(download_dir)
    print(f"Found {len(existing_files)} existing files")

    remaining = {}

    for episode, magnet in filtered.items():
        episode_str = episode.zfill(2)
        exists = False

        for file in existing_files:
            filename = get_file_name(file)
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


def download_magnets(episodes: dict, endpoint: str = "http://hancock:9200/magnet"):
    """Send magnet links to download endpoint.

    Args:
        episodes: Dictionary of episode -> magnet
        endpoint: URL to POST magnet links to
    """
    for key, magnet in episodes.items():
        print("Downloading " + magnet)

        header = {'Content-type': 'application/json'}
        data = {"magnet": magnet}
        response = requests.post(endpoint, data=json.dumps(data), headers=header)
        print(response.text)
