#!/usr/bin/env python3
"""
Media Management Service - unified CLI entry point.

This module provides the main `mms` command with subcommands for all
media management tools.
"""

import click

from mediaservice.cli.cleaner import clean_cmd
from mediaservice.cli.media_worker import worker_cmd
from mediaservice.cli.subsplease_dl import subsplease_cmd
from mediaservice.cli.erai_raws_dl import erai_cmd
from mediaservice.cli.indexer import index_cmd
from mediaservice.cli.sg_worker import sg_worker_cmd
from mediaservice.cli.sg_scrape import sg_scrape_cmd


@click.group()
@click.version_option(version="0.1.0", prog_name="mms")
def cli():
    """Media Management Service - unified CLI for media automation."""
    pass


# Register top-level commands
cli.add_command(worker_cmd, name="worker")
cli.add_command(clean_cmd, name="clean")
cli.add_command(index_cmd, name="index")


# Create download group for subsplease and erai
@cli.group()
def download():
    """Download anime from various sources."""
    pass


download.add_command(subsplease_cmd, name="subsplease")
download.add_command(erai_cmd, name="erai")


# Create sg group for SuicideGirls tools
@cli.group()
def sg():
    """SuicideGirls image tools."""
    pass


sg.add_command(sg_worker_cmd, name="worker")
sg.add_command(sg_scrape_cmd, name="scrape")


if __name__ == "__main__":
    cli()
