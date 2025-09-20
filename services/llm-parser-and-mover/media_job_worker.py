#!/usr/bin/env python3
"""
Media Job Worker - Processes media files from staging directory

This module handles processing of media files from a MongoDB queue,
using LLM prompts to determine file metadata and destination paths.
"""

import os
import shutil
import sys
import json
from datetime import datetime, UTC
from typing import Dict, Optional, Any
from pathlib import Path
import logging

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from mediaservice.ollama import run_prompt
from mediaservice.file import ismovie

# Configuration constants
STAGING_DIRECTORY = Path("/home/keeb/media/video/staging/")
DEBUG_LOG_DIRECTORY = Path("/home/keeb/media/debug/llm-responses/")
DEFAULT_MONGO_HOST = "localhost"
DEFAULT_MONGO_PORT = "27017"
DEFAULT_MONGO_USERNAME = "treehouse"
DEFAULT_MONGO_PASSWORD = "mongo"
DEFAULT_MONGO_DATABASE = "media"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def save_debug_log(
    job_id: str, filename: str, step: str, input_data: str, output_data: str
) -> None:
    """Save LLM input/output for debugging purposes.

    Args:
        job_id: ID of the job being processed
        filename: Name of the file being processed
        step: Processing step (e.g., 'filename_to_json', 'json_to_save_path')
        input_data: Input data sent to LLM
        output_data: Output data received from LLM
    """
    try:
        # Ensure debug directory exists
        DEBUG_LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

        # Create debug log entry
        debug_entry = {
            "timestamp": datetime.now().isoformat(),
            "job_id": str(job_id),
            "filename": filename,
            "step": step,
            "input": input_data,
            "output": output_data,
        }

        # Save to file named by job_id and step
        log_filename = f"{job_id}_{step}.json"
        log_path = DEBUG_LOG_DIRECTORY / log_filename

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(debug_entry, f, indent=2, ensure_ascii=False)

        logger.debug(f"Saved debug log: {log_path}")

    except Exception as e:
        logger.warning(f"Failed to save debug log: {e}")
        # Don't fail the job processing if debug logging fails


def connect_to_mongo() -> Database:
    """Connect to MongoDB using environment variables or defaults.

    Returns:
        Database: MongoDB database instance

    Raises:
        ConnectionError: If unable to connect to MongoDB
    """
    try:
        host = os.getenv("MONGO_HOST", DEFAULT_MONGO_HOST)
        port = os.getenv("MONGO_PORT", DEFAULT_MONGO_PORT)
        username = os.getenv("MONGO_USERNAME", DEFAULT_MONGO_USERNAME)
        password = os.getenv("MONGO_PASSWORD", DEFAULT_MONGO_PASSWORD)
        database = os.getenv("MONGO_DATABASE", DEFAULT_MONGO_DATABASE)

        connection_string = f"mongodb://{username}:{password}@{host}:{port}"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)

        # Test the connection
        client.server_info()

        db = client[database]
        logger.info(f"Successfully connected to MongoDB at {host}:{port}")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise ConnectionError(f"Could not connect to MongoDB: {e}") from e


def pop_job_from_queue(db: Database) -> Optional[Dict[str, Any]]:
    """Pop a pending job from the media.jobs collection and update status to in_progress.

    Args:
        db: MongoDB database instance

    Returns:
        Optional[Dict[str, Any]]: Job document if found, None otherwise

    Raises:
        Exception: If database operation fails
    """
    try:
        jobs_collection: Collection = db.jobs

        # Find a job that's pending (not in_progress and not done)
        job = jobs_collection.find_one_and_update(
            {"status": {"$in": ["pending", "queued", None]}},
            {"$set": {"status": "in_progress", "updated_at": datetime.now(UTC)}},
            return_document=True,
        )

        if job:
            logger.info(f"Picked up job {job.get('_id', 'unknown')} from queue")
        else:
            logger.debug("No pending jobs found in queue")

        return job
    except Exception as e:
        logger.error(f"Error retrieving job from queue: {e}")
        raise


def filename_to_json(filename: str, job_id: str = "unknown") -> str:
    """Convert filename to JSON metadata using LLM prompt.

    Args:
        filename: The filename to analyze
        job_id: ID of the job for debug logging

    Returns:
        str: JSON string containing file metadata

    Raises:
        Exception: If LLM prompt execution fails
    """
    try:
        logger.debug(f"Processing filename: {filename}")
        file_data = run_prompt(
            "../../prompts/filename-to-json.prompt", filename, model="qwen3:14b"
        )

        # Save debug log
        save_debug_log(job_id, filename, "filename_to_json", filename, file_data)

        logger.info(f"Generated metadata for {filename}")
        return file_data
    except Exception as e:
        logger.error(f"Failed to process filename {filename}: {e}")
        raise


def find_save_path(
    file_json: str, filename: str = "unknown", job_id: str = "unknown"
) -> str:
    """Determine save path from JSON metadata using LLM prompt.

    Args:
        file_json: JSON string containing file metadata
        filename: Original filename for debug logging
        job_id: ID of the job for debug logging

    Returns:
        str: Destination path for the file

    Raises:
        Exception: If LLM prompt execution fails
    """
    try:
        logger.debug("Determining save path from metadata")
        save_path = run_prompt(
            "../../prompts/json-to-save-path.prompt", file_json, model="qwen3:14b"
        )

        # Save debug log
        save_debug_log(job_id, filename, "json_to_save_path", file_json, save_path)

        logger.info(f"Generated save path: {save_path}")
        return save_path
    except Exception as e:
        logger.error(f"Failed to determine save path: {e}")
        raise


def move_safely(src: str, dest: str) -> None:
    """Safely move a file, creating destination directories as needed.

    This function ensures the destination directory structure exists before
    moving the file. It will create all necessary parent directories.
    It also constructs the final destination path to prevent accidental overwrites.

    Args:
        src: Source file path (must exist)
        dest: Destination directory path (file will be placed inside this directory)

    Raises:
        FileNotFoundError: If source file doesn't exist
        PermissionError: If insufficient permissions for move operation
        OSError: If file system operation fails
        FileExistsError: If destination file already exists

    Examples:
        >>> move_safely("/tmp/video.mkv", "/media/shows/series/s01/")
        # Creates /media/shows/series/s01/ if it doesn't exist, then moves file to /media/shows/series/s01/video.mkv
    """
    try:
        src_path = Path(src)
        dest_dir = Path(dest)

        # Validate source exists
        if not src_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {src}")

        # Ensure dest is treated as a directory by constructing the full destination path
        final_dest_path = dest_dir / src_path.name

        # Create destination directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory structure: {dest_dir}")

        # Check if destination file already exists to prevent overwrites
        if final_dest_path.exists():
            raise FileExistsError(f"Destination file already exists: {final_dest_path}")

        # Move the file
        shutil.move(str(src_path), str(final_dest_path))
        logger.info(f"Successfully moved {src} to {final_dest_path}")

    except Exception as e:
        logger.error(f"Failed to move file from {src} to {dest}: {e}")
        raise


def mark_job_completed(db: Database, job_id: str) -> None:
    """Mark a job as completed in the database.

    Args:
        db: MongoDB database instance
        job_id: ID of the job to mark as completed

    Raises:
        Exception: If database update fails
    """
    try:
        jobs_collection: Collection = db.jobs
        result = jobs_collection.update_one(
            {"_id": job_id},
            {"$set": {"status": "done", "completed_at": datetime.now(UTC)}},
        )

        if result.modified_count == 1:
            logger.info(f"Job {job_id} marked as completed")
        else:
            logger.warning(f"Failed to update job {job_id} status")

    except Exception as e:
        logger.error(f"Error marking job {job_id} as completed: {e}")
        raise


def mark_job_failed(db: Database, job_id: str, error_message: str) -> None:
    """Mark a job as failed in the database.

    Args:
        db: MongoDB database instance
        job_id: ID of the job to mark as failed
        error_message: Description of the failure

    Raises:
        Exception: If database update fails
    """
    try:
        jobs_collection: Collection = db.jobs
        result = jobs_collection.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "error": error_message,
                    "failed_at": datetime.now(UTC),
                }
            },
        )

        if result.modified_count == 1:
            logger.error(f"Job {job_id} marked as failed: {error_message}")
        else:
            logger.warning(f"Failed to update job {job_id} failure status")

    except Exception as e:
        logger.error(f"Error marking job {job_id} as failed: {e}")
        raise


def process_job(db: Database, job: Dict[str, Any]) -> None:
    """Process a single media job.

    Args:
        db: MongoDB database instance
        job: Job document from MongoDB

    Raises:
        Exception: If job processing fails
    """
    job_id = job.get("_id", "unknown")
    filename = job.get("name")

    if not filename:
        raise ValueError("Job missing required 'name' field")

    logger.info(f"Processing job {job_id} for file: {filename}")

    source_path = STAGING_DIRECTORY / filename

    try:
        if source_path.is_dir():
            # Process directory containing multiple files
            for file_path in source_path.iterdir():
                if file_path.is_dir():
                    # Delete subdirectories
                    logger.info(f"Deleting subdirectory: {file_path}")
                    shutil.rmtree(file_path)
                elif file_path.is_file():
                    if ismovie(str(file_path)):
                        # Process video files through LLM
                        file_json = filename_to_json(file_path.name, job_id)
                        save_path = find_save_path(file_json, file_path.name, job_id)
                        move_safely(str(file_path), save_path)
                    else:
                        # Delete non-video files
                        logger.info(f"Deleting non-video file: {file_path}")
                        file_path.unlink()

            # Remove the now-empty parent directory
            try:
                source_path.rmdir()
                logger.info(f"Removed empty directory: {source_path}")
            except OSError as e:
                logger.warning(f"Could not remove directory {source_path}: {e}")
        elif source_path.is_file():
            # Process single file
            file_json = filename_to_json(filename, job_id)
            save_path = find_save_path(file_json, filename, job_id)
            move_safely(str(source_path), save_path)
        else:
            raise FileNotFoundError(f"Source path not found: {source_path}")

        mark_job_completed(db, job_id)

    except Exception as e:
        logger.error(f"Failed to process job {job_id}: {e}")
        mark_job_failed(db, job_id, str(e))
        raise


def main() -> int:
    """Main entry point for the media job worker.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting media job worker")

        # Connect to MongoDB
        db = connect_to_mongo()

        # Pop a job from the queue
        job = pop_job_from_queue(db)

        if job:
            process_job(db, job)
        else:
            logger.info("No jobs available in the queue")

        logger.info("Media job worker completed successfully")
        return 0

    except ConnectionError as e:
        logger.critical(f"Database connection failed: {e}")
        return 1
    except Exception as e:
        logger.critical(f"Unexpected error in main: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
