#!/usr/bin/env python3
"""
CLI tool to download anime episodes from SubsPlease.

Usage:
    subsplease-dl <show name> [episode-range] [--auto]

Examples:
    subsplease-dl "dandadan"
    subsplease-dl "one piece" 1080-1090
    subsplease-dl "dandadan" --auto
"""

import sys

from mediaservice.sources.subsplease import (
    search,
    filter_results,
    filter_range,
    filter_exists,
    download_magnets,
)


# Default directories to check for existing episodes
DEFAULT_DIRS = [
    "/home/keeb/media/video/anime",
    "/home/keeb/media/video/staging",
    "/home/keeb/media/video/movies",
]


def main():
    if len(sys.argv) < 2:
        print("Usage: subsplease-dl <show name> [episodes] [--auto]")
        print("  --auto: Skip download prompt and download automatically")
        sys.exit(1)

    term = sys.argv[1]
    auto_download = "--auto" in sys.argv

    print("Searching for " + term)
    results = filter_results(search(term), "1080")

    # Check for episode range argument
    if len(sys.argv) >= 3:
        for arg in sys.argv[2:]:
            if arg != "--auto" and "-" in arg:
                start, stop = arg.split("-")
                results = filter_range(results, int(start), int(stop))
                break

    if len(results) == 0:
        print("No results found")
        sys.exit(0)

    # Filter out episodes that already exist
    for dir_path in DEFAULT_DIRS:
        results = filter_exists(results, dir_path, key_identifier=term)

        if len(results) == 0:
            print("All episodes already exist locally")
            sys.exit(0)

    print(f"Found {len(results)} episodes to download")

    if auto_download:
        print("Auto-downloading...")
        download_magnets(results)
    else:
        user_input = input("Download? (y/n): ")
        if user_input == "y":
            download_magnets(results)
        else:
            print("Not downloading")
            print(results)
            sys.exit(0)


if __name__ == "__main__":
    main()
