#!/usr/bin/env python3
"""
CLI tool to download anime episodes from Erai-raws via Nyaa RSS.

Usage:
    mms download erai <show name> [--auto] [--lang EN]
    mms download erai --config path/to/shows.yaml [--auto]
"""

import sys

import click
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
    dirs: list[str] | None = None,
    show_config: dict | None = None,
) -> None:
    """Process a single show - search and optionally download."""
    if dirs is None:
        dirs = DEFAULT_DIRS

    click.echo(f"\n{'='*60}")
    click.echo(f"Processing: {name}")
    click.echo(f"Resolution: {resolution}, Language: {language}")
    if show_config and show_config.get("seasons"):
        click.echo(f"Season config: {len(show_config['seasons'])} seasons defined")
    click.echo(f"{'='*60}")

    episodes = search_show(
        name,
        resolution=resolution,
        language=language,
        dirs=dirs,
        filter_existing=True,
        show_config=show_config,
    )

    if not episodes:
        click.echo("No new episodes to download")
        return

    click.echo(f"\nFound {len(episodes)} new episodes:")
    for ep in episodes:
        click.echo(f"  - Episode {ep.episode}: {ep.title}")

    if auto_download:
        click.echo("\nAuto-downloading...")
        download_magnets(episodes)
    else:
        if click.confirm("\nDownload?"):
            download_magnets(episodes)
        else:
            click.echo("Not downloading")


def load_config(config_path: str) -> list[dict]:
    """Load shows configuration from YAML file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config.get("shows", [])


@click.command("erai")
@click.argument("show", required=False)
@click.option("--config", "config_path", default=None, help="Path to YAML config file with show list")
@click.option("--lang", default="JA", help="Language code to filter for (default: JA)")
@click.option("--auto", is_flag=True, help="Skip download prompt and download automatically")
def erai_cmd(show: str | None, config_path: str | None, lang: str, auto: bool):
    """Download anime episodes from Erai-raws."""
    if config_path:
        # Config mode - process all shows from file
        click.echo(f"Loading config from: {config_path}")
        shows = load_config(config_path)

        if not shows:
            click.echo("No shows found in config")
            sys.exit(1)

        click.echo(f"Found {len(shows)} shows to process")

        for show_entry in shows:
            name = show_entry.get("name")
            resolution = show_entry.get("resolution", "1080p")
            language = show_entry.get("language", "EN")

            if not name:
                click.echo("Skipping show with no name")
                continue

            process_show(
                name,
                resolution=resolution,
                language=language,
                auto_download=auto,
                show_config=show_entry,
            )
    elif show:
        # Single show mode
        process_show(show, language=lang, auto_download=auto)
    else:
        click.echo("Error: Either provide a show name or use --config")
        sys.exit(1)


def main():
    """Legacy entry point."""
    erai_cmd()


if __name__ == "__main__":
    main()
