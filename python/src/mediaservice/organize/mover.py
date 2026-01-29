#!/usr/bin/env python3
"""
Media Job Worker - Processes media files from staging directory

This module handles processing of media files from a MongoDB queue,
using LLM prompts to determine file metadata and destination paths.
"""

import os
import shutil
import json
from datetime import datetime, UTC
from typing import Dict, Optional, Any
from pathlib import Path
import logging

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from mediaservice.util.ollama import run_prompt
from mediaservice.util.file import ismovie

# Configuration constants
STAGING_DIRECTORY = Path("/home/keeb/media/video/staging/")
DEBUG_LOG_DIRECTORY = Path("/home/keeb/media/debug/llm-responses/")
DEFAULT_MONGO_HOST = "localhost"
DEFAULT_MONGO_PORT = "27017"
DEFAULT_MONGO_USERNAME = "treehouse"
DEFAULT_MONGO_PASSWORD = "mongo"
DEFAULT_MONGO_DATABASE = "media"
DEFAULT_MAX_JOBS_PER_RUN = 0  # 0 means unlimited (process all available jobs)

# Configure logging
logger = logging.getLogger(__name__)


def save_debug_log(
    job_id: str, filename: str, step: str, input_data: str, output_data: str
) -> None:
    """Save LLM input/output for debugging purposes."""
    try:
        DEBUG_LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

        debug_entry = {
            "timestamp": datetime.now().isoformat(),
            "job_id": str(job_id),
            "filename": filename,
            "step": step,
            "input": input_data,
            "output": output_data,
        }

        log_filename = f"{job_id}_{step}.json"
        log_path = DEBUG_LOG_DIRECTORY / log_filename

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(debug_entry, f, indent=2, ensure_ascii=False)

        logger.debug(f"Saved debug log: {log_path}")

    except Exception as e:
        logger.warning(f"Failed to save debug log: {e}")


def connect_to_mongo() -> Database:
    """Connect to MongoDB using environment variables or defaults."""
    try:
        host = os.getenv("MONGO_HOST", DEFAULT_MONGO_HOST)
        port = os.getenv("MONGO_PORT", DEFAULT_MONGO_PORT)
        username = os.getenv("MONGO_USERNAME", DEFAULT_MONGO_USERNAME)
        password = os.getenv("MONGO_PASSWORD", DEFAULT_MONGO_PASSWORD)
        database = os.getenv("MONGO_DATABASE", DEFAULT_MONGO_DATABASE)

        connection_string = f"mongodb://{username}:{password}@{host}:{port}"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)

        client.server_info()

        db = client[database]
        logger.info(f"Successfully connected to MongoDB at {host}:{port}")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise ConnectionError(f"Could not connect to MongoDB: {e}") from e


def pop_job_from_queue(db: Database) -> Optional[Dict[str, Any]]:
    """Pop a pending job from the media.jobs collection and update status to in_progress."""
    try:
        jobs_collection: Collection = db.jobs

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


def filename_to_json(filename: str, job_id: str = "unknown", prompts_dir: str = "prompts") -> str:
    """Convert filename to JSON metadata using LLM prompt."""
    try:
        logger.debug(f"Processing filename: {filename}")
        prompt_path = os.path.join(prompts_dir, "filename-to-json.prompt")
        file_data = run_prompt(prompt_path, filename, model="qwen3:14b")

        save_debug_log(job_id, filename, "filename_to_json", filename, file_data)

        logger.info(f"Generated metadata for {filename}")
        return file_data
    except Exception as e:
        logger.error(f"Failed to process filename {filename}: {e}")
        raise


def find_save_path(
    file_json: str, filename: str = "unknown", job_id: str = "unknown", prompts_dir: str = "prompts"
) -> str:
    """Determine save path from JSON metadata using LLM prompt."""
    try:
        logger.debug("Determining save path from metadata")
        prompt_path = os.path.join(prompts_dir, "json-to-save-path.prompt")
        save_path = run_prompt(prompt_path, file_json, model="qwen3:14b")

        save_debug_log(job_id, filename, "json_to_save_path", file_json, save_path)

        logger.info(f"Generated save path: {save_path}")
        return save_path
    except Exception as e:
        logger.error(f"Failed to determine save path: {e}")
        raise


def move_safely(src: str, dest: str) -> None:
    """Safely move a file, creating destination directories as needed."""
    try:
        src_path = Path(src)
        dest_dir = Path(dest)

        if not src_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {src}")

        final_dest_path = dest_dir / src_path.name

        dest_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory structure: {dest_dir}")

        if final_dest_path.exists():
            raise FileExistsError(f"Destination file already exists: {final_dest_path}")

        shutil.move(str(src_path), str(final_dest_path))
        logger.info(f"Successfully moved {src} to {final_dest_path}")

    except Exception as e:
        logger.error(f"Failed to move file from {src} to {dest}: {e}")
        raise


def mark_job_completed(db: Database, job_id: str) -> None:
    """Mark a job as completed in the database."""
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
    """Mark a job as failed in the database."""
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


def process_job(db: Database, job: Dict[str, Any], prompts_dir: str = "prompts") -> None:
    """Process a single media job."""
    job_id = job.get("_id", "unknown")
    filename = job.get("name")

    if not filename:
        raise ValueError("Job missing required 'name' field")

    logger.info(f"Processing job {job_id} for file: {filename}")

    source_path = STAGING_DIRECTORY / filename

    try:
        if source_path.is_dir():
            for file_path in source_path.iterdir():
                if file_path.is_dir():
                    logger.info(f"Deleting subdirectory: {file_path}")
                    shutil.rmtree(file_path)
                elif file_path.is_file():
                    if ismovie(str(file_path)):
                        file_json = filename_to_json(file_path.name, job_id, prompts_dir)
                        save_path = find_save_path(file_json, file_path.name, job_id, prompts_dir)
                        move_safely(str(file_path), save_path)
                    else:
                        logger.info(f"Deleting non-video file: {file_path}")
                        file_path.unlink()

            try:
                source_path.rmdir()
                logger.info(f"Removed empty directory: {source_path}")
            except OSError as e:
                logger.warning(f"Could not remove directory {source_path}: {e}")
        elif source_path.is_file():
            file_json = filename_to_json(filename, job_id, prompts_dir)
            save_path = find_save_path(file_json, filename, job_id, prompts_dir)
            move_safely(str(source_path), save_path)
        else:
            raise FileNotFoundError(f"Source path not found: {source_path}")

        mark_job_completed(db, job_id)

    except Exception as e:
        logger.error(f"Failed to process job {job_id}: {e}")
        mark_job_failed(db, job_id, str(e))
        raise


def run_worker(max_jobs: int = 0, prompts_dir: str = "prompts") -> tuple[int, int]:
    """Run the media worker, processing jobs from the queue.

    Args:
        max_jobs: Maximum jobs to process (0 = unlimited)
        prompts_dir: Directory containing LLM prompt files

    Returns:
        Tuple of (jobs_processed, failures)
    """
    db = connect_to_mongo()

    jobs_processed = 0
    total_failures = 0

    logger.info(f"Processing jobs (max: {'unlimited' if max_jobs == 0 else max_jobs})")

    while max_jobs == 0 or jobs_processed < max_jobs:
        job = pop_job_from_queue(db)

        if not job:
            logger.info("No more jobs available in the queue")
            break

        try:
            process_job(db, job, prompts_dir)
            jobs_processed += 1
            logger.info(f"Processed {jobs_processed} jobs so far")
        except Exception as e:
            total_failures += 1
            logger.error(f"Job processing failed: {e}")

    return jobs_processed, total_failures
