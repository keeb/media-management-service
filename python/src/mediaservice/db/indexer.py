"""
Media indexing utilities for MongoDB.
"""

import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


def get_mongo_client():
    """Get MongoDB client from environment or defaults."""
    host = os.environ.get("MONGO_HOST", "localhost")
    port = os.environ.get("MONGO_PORT", "27017")
    username = os.environ.get("MONGO_USERNAME", "treehouse")
    password = os.environ.get("MONGO_PASSWORD", "mongo")
    return MongoClient(f"mongodb://{username}:{password}@{host}:{port}")


def get_media_collection():
    """Get the media collection."""
    client = get_mongo_client()
    db = client.media_management
    return db.media


def create_media_collection():
    """Create media collection if it doesn't exist with unique index."""
    try:
        collection = get_media_collection()
        collection.create_index("file_path", unique=True)
        print("Media collection created/verified with unique index on file_path")
    except Exception as e:
        print(f"Collection setup: {e}")


def generate_file_hash(file_path: str, file_size: Optional[int] = None) -> str:
    """Generate a simple hash for the file based on path and size."""
    hash_input = f"{file_path}:{file_size or 0}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def insert_media_record(
    file_path: str,
    file_name: Optional[str] = None,
    file_size: Optional[int] = None,
    media_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Insert a new media record into the collection.

    Args:
        file_path: Full path to the media file (required, used for uniqueness)
        file_name: Name of the file (optional, will extract from path if not provided)
        file_size: Size of the file in bytes (optional)
        media_type: Type of media (video, image, audio, etc.) (optional)
        tags: List of tags for the media (optional)
        metadata: Additional metadata for the media (optional)

    Returns:
        Result of the insert operation
    """
    if not file_path:
        return {"error": "file_path is required"}

    if not file_name:
        file_name = os.path.basename(file_path)

    media_record = {
        "file_path": file_path,
        "file_name": file_name,
        "file_hash": generate_file_hash(file_path, file_size),
        "file_size": file_size,
        "media_type": media_type,
        "tags": tags or [],
        "metadata": metadata or {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        collection = get_media_collection()
        result = collection.insert_one(media_record)
        return {
            "success": True,
            "inserted_id": str(result.inserted_id),
            "record": media_record
        }
    except DuplicateKeyError:
        return {
            "error": "Duplicate record - file_path already exists",
            "file_path": file_path
        }
    except Exception as e:
        return {
            "error": f"Insert failed: {str(e)}",
            "file_path": file_path
        }


def update_media_record(file_path: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing media record.

    Args:
        file_path: Path of the record to update
        updates: Fields to update

    Returns:
        Result of the update operation
    """
    updates["updated_at"] = datetime.utcnow()

    try:
        collection = get_media_collection()
        result = collection.update_one(
            {"file_path": file_path},
            {"$set": updates}
        )

        if result.matched_count == 0:
            return {"error": "No record found with that file_path"}

        return {
            "success": True,
            "modified_count": result.modified_count
        }
    except Exception as e:
        return {"error": f"Update failed: {str(e)}"}


def get_media_record(file_path: str) -> Dict[str, Any]:
    """Get a media record by file path."""
    try:
        collection = get_media_collection()
        record = collection.find_one({"file_path": file_path})
        if record:
            record["_id"] = str(record["_id"])
            return {"success": True, "record": record}
        else:
            return {"error": "Record not found"}
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


def list_media_records(
    limit: int = 10,
    skip: int = 0,
    media_type: Optional[str] = None
) -> Dict[str, Any]:
    """List media records with optional filtering."""
    try:
        collection = get_media_collection()
        query = {}
        if media_type:
            query["media_type"] = media_type

        cursor = collection.find(query).skip(skip).limit(limit)
        records = []
        for record in cursor:
            record["_id"] = str(record["_id"])
            records.append(record)

        total_count = collection.count_documents(query)

        return {
            "success": True,
            "records": records,
            "total_count": total_count,
            "returned_count": len(records)
        }
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}
