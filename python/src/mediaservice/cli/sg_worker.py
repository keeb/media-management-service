#!/usr/bin/env python3
"""
CLI tool to download queued SuicideGirls images.

Processes work items from MongoDB pending queue, downloads images,
and saves them organized by model/album structure.
"""

import os
import sys

from mediaservice.download.images import process_work


def main():
    """Main entry point for SG worker."""
    output_directory = os.environ.get("SG_OUTPUT_DIR", os.path.join(os.getcwd(), "static/save"))

    print(f"SG Worker starting, output directory: {output_directory}")

    try:
        process_work(output_directory)
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
