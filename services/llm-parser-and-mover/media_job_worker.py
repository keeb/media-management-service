#!/usr/bin/env python3

import sys

from pymongo import MongoClient
import json
from datetime import datetime
from mediaservice.ollama import run_prompt

def connect_to_mongo():
    """Connect to MongoDB using credentials from docker-compose.yml"""
    client = MongoClient("mongodb://treehouse:mongo@localhost:27017")
    db = client.media
    return db

def pop_job_from_queue(db):
    """Pop a job from the media.jobs collection and update status to in_progress"""
    jobs_collection = db.jobs
    
    # Find a job that's not in progress
    # TODO: WHAT ABOUT JOBS THAT ARE DONE?
    job = jobs_collection.find_one_and_update(
        {"status": {"$ne": "in_progress"}},
        {
            "$set": {
                #"status": "in_progress",
                "updated_at": datetime.utcnow()
            }
        },
        return_document=True
    )
    
    return job

def main():
    try:
        # Connect to MongoDB
        db = connect_to_mongo()
        print("Connected to MongoDB successfully")
        
        # Pop a job from the queue
        job = pop_job_from_queue(db)
        
        if job:
            filename = job["name"]
            print(f"found file to process filename")
            file_data = run_prompt("../../prompts/filename-to-json.prompt", filename)
            print(file_data)

        else:
            print("No jobs available in the queue")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
