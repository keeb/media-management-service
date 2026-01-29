#!/usr/bin/env python3
"""
CLI tool to index media files to MongoDB.
"""

import sys

import click

from mediaservice.db.indexer import (
    create_media_collection,
    insert_media_record,
    list_media_records,
)


@click.group("index")
def index_cmd():
    """Index and manage media files in MongoDB."""
    # Initialize collection on any index command
    create_media_collection()


@index_cmd.command("list")
@click.option("--limit", default=10, help="Number of records to show")
def index_list(limit: int):
    """List indexed media files."""
    result = list_media_records(limit=limit)
    if result.get("success"):
        click.echo(f"Found {result['total_count']} total records:")
        for record in result["records"]:
            click.echo(f"  - {record['file_path']} ({record.get('media_type', 'unknown')})")
    else:
        click.echo(f"Error: {result.get('error')}")
        sys.exit(1)


@index_cmd.command("add")
@click.argument("file_path")
@click.option("--type", "media_type", default=None, help="Media type (anime, movie, etc.)")
def index_add(file_path: str, media_type: str | None):
    """Add a file to the media index."""
    result = insert_media_record(file_path=file_path, media_type=media_type)
    if result.get("success"):
        click.echo(f"Indexed: {file_path}")
    else:
        click.echo(f"Error: {result.get('error')}")
        sys.exit(1)


@index_cmd.command("status")
def index_status():
    """Show current index status."""
    result = list_media_records(limit=5)
    if result.get("success"):
        click.echo(f"Current index contains {result['total_count']} records")
        if result["records"]:
            click.echo("\nRecent entries:")
            for record in result["records"]:
                click.echo(f"  - {record['file_path']} ({record.get('media_type', 'unknown')})")
    else:
        click.echo(f"Error: {result.get('error')}")
        sys.exit(1)


def main():
    """Legacy entry point for media indexer."""
    click.echo("Media Indexer")
    click.echo("=============")

    # Initialize collection
    create_media_collection()

    # Parse command line arguments for legacy support
    if len(sys.argv) < 2:
        click.echo("\nUsage:")
        click.echo("  media-indexer list [limit]     - List indexed media")
        click.echo("  media-indexer add <file_path>  - Add a file to the index")
        click.echo()

        # Show current index status
        result = list_media_records(limit=5)
        if result.get("success"):
            click.echo(f"Current index contains {result['total_count']} records")
            if result["records"]:
                click.echo("\nRecent entries:")
                for record in result["records"]:
                    click.echo(
                        f"  - {record['file_path']} ({record.get('media_type', 'unknown')})"
                    )
        return 0

    command = sys.argv[1]

    if command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = list_media_records(limit=limit)
        if result.get("success"):
            click.echo(f"Found {result['total_count']} total records:")
            for record in result["records"]:
                click.echo(
                    f"  - {record['file_path']} ({record.get('media_type', 'unknown')})"
                )
        else:
            click.echo(f"Error: {result.get('error')}")
            return 1

    elif command == "add":
        if len(sys.argv) < 3:
            click.echo("Error: file_path required")
            return 1

        file_path = sys.argv[2]
        media_type = sys.argv[3] if len(sys.argv) > 3 else None

        result = insert_media_record(file_path=file_path, media_type=media_type)
        if result.get("success"):
            click.echo(f"Indexed: {file_path}")
        else:
            click.echo(f"Error: {result.get('error')}")
            return 1

    else:
        click.echo(f"Unknown command: {command}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
