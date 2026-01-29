#!/usr/bin/env python3
"""
CLI tool to index media files to MongoDB.
"""

import sys

from mediaservice.db.indexer import (
    create_media_collection,
    insert_media_record,
    list_media_records,
)


def main():
    """Main entry point for media indexer."""
    print("Media Indexer")
    print("=============")

    # Initialize collection
    create_media_collection()

    # Parse command line arguments
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  media-indexer list [limit]     - List indexed media")
        print("  media-indexer add <file_path>  - Add a file to the index")
        print()

        # Show current index status
        result = list_media_records(limit=5)
        if result.get("success"):
            print(f"Current index contains {result['total_count']} records")
            if result["records"]:
                print("\nRecent entries:")
                for record in result["records"]:
                    print(f"  - {record['file_path']} ({record.get('media_type', 'unknown')})")
        return 0

    command = sys.argv[1]

    if command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = list_media_records(limit=limit)
        if result.get("success"):
            print(f"Found {result['total_count']} total records:")
            for record in result["records"]:
                print(f"  - {record['file_path']} ({record.get('media_type', 'unknown')})")
        else:
            print(f"Error: {result.get('error')}")
            return 1

    elif command == "add":
        if len(sys.argv) < 3:
            print("Error: file_path required")
            return 1

        file_path = sys.argv[2]
        media_type = sys.argv[3] if len(sys.argv) > 3 else None

        result = insert_media_record(file_path=file_path, media_type=media_type)
        if result.get("success"):
            print(f"Indexed: {file_path}")
        else:
            print(f"Error: {result.get('error')}")
            return 1

    else:
        print(f"Unknown command: {command}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
