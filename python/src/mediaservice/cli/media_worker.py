#!/usr/bin/env python3
"""
CLI tool for LLM-based media file categorization and moving.

Processes media files from a staging directory, uses LLM to determine
metadata and destination paths, then moves files to their final locations.
"""

import sys
import os
import logging

import click

from mediaservice.organize.mover import run_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@click.command("worker")
@click.option("--max-jobs", default=0, help="Maximum jobs to process (0 = unlimited)")
@click.option("--prompts-dir", default=None, help="Directory containing LLM prompts")
def worker_cmd(max_jobs: int, prompts_dir: str | None):
    """Run the media worker to process queued files."""
    try:
        logger.info("Starting media job worker")

        # Get configuration from environment if not provided
        if max_jobs == 0:
            max_jobs = int(os.getenv("MAX_JOBS_PER_RUN", "0"))
        if prompts_dir is None:
            prompts_dir = os.getenv("PROMPTS_DIR", "prompts")

        jobs_processed, total_failures = run_worker(max_jobs, prompts_dir)

        logger.info(
            f"Media job worker completed - Processed: {jobs_processed}, Failed: {total_failures}"
        )
        sys.exit(0)

    except ConnectionError as e:
        logger.critical(f"Database connection failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error in main: {e}")
        sys.exit(1)


def main() -> int:
    """Legacy entry point for the media job worker."""
    worker_cmd()
    return 0


if __name__ == "__main__":
    main()
