#!/usr/bin/env python3
"""
Media Insert Script
Simple script to insert distinct records into the media collection
"""

import sys
import os

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
import hashlib

# MongoDB connection (using localhost since we're connecting to Docker container)
client = MongoClient("mongodb://treehouse:mongo@localhost:27017")
db = client.media_management
media_collection = db.media

def create_media_collection():
    """Create media collection if it doesn't exist"""
    try:
        # Create collection with unique index on file_path to prevent duplicates
        media_collection.create_index("file_path", unique=True)
        print("Media collection created/verified with unique index on file_path")
    except Exception as e:
        print(f"Collection setup: {e}")

def generate_file_hash(file_path, file_size=None):
    """Generate a simple hash for the file based on path and size"""
    hash_input = f"{file_path}:{file_size or 0}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def insert_media_record(file_path, file_name=None, file_size=None, media_type=None, 
                       tags=None, metadata=None):
    """
    Insert a new media record into the collection
    
    Args:
        file_path (str): Full path to the media file (required, used for uniqueness)
        file_name (str): Name of the file (optional, will extract from path if not provided)
        file_size (int): Size of the file in bytes (optional)
        media_type (str): Type of media (video, image, audio, etc.) (optional)
        tags (list): List of tags for the media (optional)
        metadata (dict): Additional metadata for the media (optional)
    
    Returns:
        dict: Result of the insert operation
    """
    if not file_path:
        return {"error": "file_path is required"}
    
    # Extract file name from path if not provided
    if not file_name:
        file_name = os.path.basename(file_path)
    
    # Create the media record
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
        # Insert the record
        result = media_collection.insert_one(media_record)
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

def update_media_record(file_path, updates):
    """
    Update an existing media record
    
    Args:
        file_path (str): Path of the record to update
        updates (dict): Fields to update
    
    Returns:
        dict: Result of the update operation
    """
    updates["updated_at"] = datetime.utcnow()
    
    try:
        result = media_collection.update_one(
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

def get_media_record(file_path):
    """Get a media record by file path"""
    try:
        record = media_collection.find_one({"file_path": file_path})
        if record:
            record["_id"] = str(record["_id"])  # Convert ObjectId to string
            return {"success": True, "record": record}
        else:
            return {"error": "Record not found"}
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}

def list_media_records(limit=10, skip=0, media_type=None):
    """List media records with optional filtering"""
    try:
        query = {}
        if media_type:
            query["media_type"] = media_type
        
        cursor = media_collection.find(query).skip(skip).limit(limit)
        records = []
        for record in cursor:
            record["_id"] = str(record["_id"])
            records.append(record)
        
        total_count = media_collection.count_documents(query)
        
        return {
            "success": True,
            "records": records,
            "total_count": total_count,
            "returned_count": len(records)
        }
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}

def main():
    """Example usage of the media insert functions"""
    print("Media Insert Script")
    print("==================")
    
    # Initialize collection
    create_media_collection()
    
    # Example insertions
    examples = [
        {
            "file_path": "/home/user/videos/example1.mp4",
            "file_size": 1024000,
            "media_type": "video",
            "tags": ["example", "test"],
            "metadata": {"duration": "00:02:30", "resolution": "1920x1080"}
        },
        {
            "file_path": "/home/user/images/photo1.jpg",
            "file_size": 512000,
            "media_type": "image", 
            "tags": ["photo", "test"],
            "metadata": {"resolution": "1920x1080", "camera": "Canon"}
        }
    ]
    
    print("\nInserting example records:")
    for example in examples:
        result = insert_media_record(**example)
        if result.get("success"):
            print(f"✓ Inserted: {example['file_path']}")
        else:
            print(f"✗ Failed: {example['file_path']} - {result.get('error')}")
    
    print("\nListing all records:")
    result = list_media_records()
    if result.get("success"):
        print(f"Found {result['total_count']} total records:")
        for record in result["records"]:
            print(f"  - {record['file_path']} ({record.get('media_type', 'unknown')})")
    else:
        print(f"Failed to list records: {result.get('error')}")

if __name__ == "__main__":
    main()
