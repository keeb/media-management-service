#!/usr/bin/env python3
"""
CLI tool for LLM-based media file categorization and moving.

Processes media files from a staging directory, uses LLM to determine
metadata and destination paths, then moves files to their final locations.
"""

import sys
import os
import logging

from mediaservice.organize.mover import run_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for the media job worker.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting media job worker")

        # Get configuration from environment
        max_jobs = int(os.getenv("MAX_JOBS_PER_RUN", "0"))
        prompts_dir = os.getenv("PROMPTS_DIR", "prompts")

        jobs_processed, total_failures = run_worker(max_jobs, prompts_dir)

        logger.info(f"Media job worker completed - Processed: {jobs_processed}, Failed: {total_failures}")
        return 0

    except ConnectionError as e:
        logger.critical(f"Database connection failed: {e}")
        return 1
    except Exception as e:
        logger.critical(f"Unexpected error in main: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
