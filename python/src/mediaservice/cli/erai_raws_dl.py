#!/usr/bin/env python3
"""
CLI tool to download anime episodes from Erai-raws via Nyaa RSS.

Usage:
    erai-raws-dl <show name> [--auto]
    erai-raws-dl --config path/to/shows.yaml [--auto]

Examples:
    erai-raws-dl "jujutsu kaisen"
    erai-raws-dl "dragon raja" --auto
    erai-raws-dl --config erai-raws-shows.yaml --auto
"""

import sys
import yaml

from mediaservice.sources.erai_raws import search_show, download_magnets


# Default directories to check for existing episodes
DEFAULT_DIRS = [
    "/home/keeb/media/video/anime/completed",
    "/home/keeb/media/video/anime",
    "/home/keeb/media/video/staging",
    "/home/keeb/media/video/movies",
]


def process_show(
    name: str,
    resolution: str = "1080p",
    language: str = "EN",
    auto_download: bool = False,
    dirs: list[str] = None,
    show_config: dict = None,
) -> None:
    """Process a single show - search and optionally download.

    Args:
        name: Show name to search for
        resolution: Resolution to filter for
        language: Language code to filter for (e.g., "EN", "JA")
        auto_download: Whether to download automatically
        dirs: Directories to check for existing files
        show_config: Optional show configuration with season mappings
    """
    if dirs is None:
        dirs = DEFAULT_DIRS

    print(f"\n{'='*60}")
    print(f"Processing: {name}")
    print(f"Resolution: {resolution}, Language: {language}")
    if show_config and show_config.get("seasons"):
        print(f"Season config: {len(show_config['seasons'])} seasons defined")
    print(f"{'='*60}")

    episodes = search_show(
        name,
        resolution=resolution,
        language=language,
        dirs=dirs,
        filter_existing=True,
        show_config=show_config,
    )

    if not episodes:
        print("No new episodes to download")
        return

    print(f"\nFound {len(episodes)} new episodes:")
    for ep in episodes:
        print(f"  - Episode {ep.episode}: {ep.title}")

    if auto_download:
        print("\nAuto-downloading...")
        download_magnets(episodes)
    else:
        user_input = input("\nDownload? (y/n): ")
        if user_input.lower() == "y":
            download_magnets(episodes)
        else:
            print("Not downloading")


def load_config(config_path: str) -> list[dict]:
    """Load shows configuration from YAML file.

    Args:
        config_path: Path to YAML config file

    Returns:
        List of show configurations
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config.get("shows", [])


def main():
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print("Usage: erai-raws-dl <show name> [--lang EN] [--auto]")
        print("       erai-raws-dl --config path/to/shows.yaml [--auto]")
        print()
        print("Options:")
        print("  --auto     Skip download prompt and download automatically")
        print("  --config   Path to YAML config file with show list")
        print("  --lang     Language code to filter for (default: JA)")
        sys.exit(0)

    auto_download = "--auto" in args
    config_path = None
    language = "JA"

    # Parse arguments with values
    for i, arg in enumerate(args):
        if arg == "--config" and i + 1 < len(args):
            config_path = args[i + 1]
        elif arg == "--lang" and i + 1 < len(args):
            language = args[i + 1]

    if config_path:
        # Config mode - process all shows from file
        print(f"Loading config from: {config_path}")
        shows = load_config(config_path)

        if not shows:
            print("No shows found in config")
            sys.exit(1)

        print(f"Found {len(shows)} shows to process")

        for show in shows:
            name = show.get("name")
            resolution = show.get("resolution", "1080p")
            language = show.get("language", "EN")

            if not name:
                print("Skipping show with no name")
                continue

            process_show(
                name,
                resolution=resolution,
                language=language,
                auto_download=auto_download,
                show_config=show,
            )
    else:
        # Single show mode
        # Collect all non-flag args as the show name (excluding values for --lang/--config)
        skip_next = False
        show_parts = []
        for i, arg in enumerate(args):
            if skip_next:
                skip_next = False
                continue
            if arg in ("--lang", "--config"):
                skip_next = True
                continue
            if not arg.startswith("--"):
                show_parts.append(arg)

        if not show_parts:
            print("Error: No show name provided")
            sys.exit(1)

        show_name = " ".join(show_parts)
        process_show(show_name, language=language, auto_download=auto_download)


if __name__ == "__main__":
    main()
