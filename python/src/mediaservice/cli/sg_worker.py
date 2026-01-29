#!/usr/bin/env python3
"""
CLI tool to download queued SuicideGirls images.

Processes work items from MongoDB pending queue, downloads images,
and saves them organized by model/album structure.
"""

import os
import sys

import click

from mediaservice.download.images import process_work


@click.command("worker")
@click.option(
    "--output-dir",
    default=None,
    help="Output directory for downloaded images",
)
def sg_worker_cmd(output_dir: str | None):
    """Run the SG image download worker."""
    if output_dir is None:
        output_dir = os.environ.get("SG_OUTPUT_DIR", os.path.join(os.getcwd(), "static/save"))

    click.echo(f"SG Worker starting, output directory: {output_dir}")

    try:
        process_work(output_dir)
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


def main():
    """Legacy entry point for SG worker."""
    sg_worker_cmd()


if __name__ == "__main__":
    main()
