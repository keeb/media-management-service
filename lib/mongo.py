from pymongo import MongoClient

client = MongoClient("mongodb://treehouse:mongo@treehouse.local:27017")
db = client.sg

def get_db():
    return db

def get_pending_queue():
    return db.pending

def get_completed_jobs():
    return db.completed




