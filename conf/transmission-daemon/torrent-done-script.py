#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from pymongo import MongoClient

client = MongoClient("mongodb://treehouse:mongo@localhost:27017")
db = client.media

def main():
    # Transmission passes environment variables to the script
    # TR_TORRENT_NAME contains the name of the completed torrent
    torrent_name = os.environ.get('TR_TORRENT_NAME')
    #torrent_dir = os.environ.get('TR_TORRENT_DIR', '/mnt/nami/media/video/staging')
    torrent_dir = os.environ.get('TR_TORRENT_DIR', '/home/keeb/media/video/staging')
    
    if not torrent_name:
        print("Error: TR_TORRENT_NAME not found in environment", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Get database connection
        jobs_collection = db.jobs
        
        # Create job document
        job_document = {
            'name': torrent_name,
            'directory': torrent_dir,
            'completed_at': datetime.utcnow(),
            'status': 'pending',
            'source': 'transmission'
        }
        
        # Insert job into media.jobs collection
        result = jobs_collection.insert_one(job_document)
        
        print(f"Successfully inserted job for '{torrent_name}' with ID: {result.inserted_id}")
        
    except Exception as e:
        print(f"Error inserting job into MongoDB: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
