#!/usr/bin/env python3
"""
CLI tool to download anime episodes from SubsPlease.

Usage:
    mms download subsplease <show name> [--range 1080-1090] [--auto]
"""

import sys

import click

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


@click.command("subsplease")
@click.argument("show")
@click.option("--range", "episode_range", default=None, help="Episode range (e.g., 1080-1090)")
@click.option("--auto", is_flag=True, help="Skip download prompt and download automatically")
def subsplease_cmd(show: str, episode_range: str | None, auto: bool):
    """Download anime episodes from SubsPlease."""
    click.echo(f"Searching for {show}")
    results = filter_results(search(show), "1080")

    # Apply episode range filter if provided
    if episode_range and "-" in episode_range:
        start, stop = episode_range.split("-")
        results = filter_range(results, int(start), int(stop))

    if len(results) == 0:
        click.echo("No results found")
        sys.exit(0)

    # Filter out episodes that already exist
    for dir_path in DEFAULT_DIRS:
        results = filter_exists(results, dir_path, key_identifier=show)

        if len(results) == 0:
            click.echo("All episodes already exist locally")
            sys.exit(0)

    click.echo(f"Found {len(results)} episodes to download")

    if auto:
        click.echo("Auto-downloading...")
        download_magnets(results)
    else:
        if click.confirm("Download?"):
            download_magnets(results)
        else:
            click.echo("Not downloading")
            click.echo(str(results))
            sys.exit(0)


def main():
    """Legacy entry point."""
    # For backwards compatibility with the old CLI that used positional args
    if len(sys.argv) < 2:
        click.echo("Usage: subsplease-dl <show name> [episodes] [--auto]")
        click.echo("  --auto: Skip download prompt and download automatically")
        sys.exit(1)
    subsplease_cmd()


if __name__ == "__main__":
    main()
