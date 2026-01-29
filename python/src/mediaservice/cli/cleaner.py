#!/usr/bin/env python3
"""
CLI tool to clean completed torrents from Transmission.
"""

import json

import click

from mediaservice.download.transmission import TransmissionRequest


@click.command("clean")
def clean_cmd():
    """Clean completed torrents from Transmission."""
    t = TransmissionRequest()

    click.echo("Checking current torrents...")
    r = t.get_torrents()
    if r.status_code == 200:
        data = json.loads(r.text)
        torrents = data.get("arguments", {}).get("torrents", [])
        click.echo(f"Found {len(torrents)} torrents")
        for torrent in torrents:
            click.echo(f'  ID: {torrent.get("id")}, Name: {torrent.get("name", "unnamed")}')

    click.echo()
    click.echo("Removing completed torrents...")

    result = t.remove_complete_torrents()

    if result and result.status_code == 200:
        click.echo("Success!")

        # Check torrents after removal
        check_result = t.get_torrents()
        if check_result.status_code == 200:
            check_data = json.loads(check_result.text)
            remaining = check_data.get("arguments", {}).get("torrents", [])
            click.echo(f"Remaining torrents: {len(remaining)}")

    elif result:
        click.echo(f"Error: Status {result.status_code}")
        click.echo(f"Response: {result.text}")
    else:
        click.echo("No completed torrents found to remove")


def main():
    """Legacy entry point."""
    clean_cmd()


if __name__ == "__main__":
    main()
