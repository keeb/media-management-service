import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

def get_db():
    return db

def get_pending_queue():
    return db.pending

def get_completed_jobs():
    return db.completed

def construct_key(model_name, album_name):
    key = {
        "model": model_name,
        "album": album_name
    }

    return key

def save(payload):
    model_name = payload.get("model")
    album_name = payload.get("album")
    queue = get_pending_queue()
    completed = get_completed_jobs()

    print("looking to see if this payload is already enqueued")
    import pprint
    key = construct_key(model_name, album_name)
    pending = queue.find_one(key)
    if pending is not None:
        print("found in pending")
        return
    
    completed = completed.find_one(key)
    if completed is not None:
        print("found in completed")
        return

    print ("it isn't. adding")
    queue.insert_one(payload)

def handle(payload):
    model_name = payload.get("model")
    album_name = payload.get("album")
    image_list = payload.get("images")
    socials_list = payload.get("socials")
    print("received model: %s" % model_name)
    print("received album: %s" % album_name)
    print("received number of images %s" % len(image_list))
    print("received number of socials %s" % len(socials_list))

    save(payload)

    return

app = Flask(__name__)
CORS(app)
client = MongoClient("mongodb://treehouse:mongo@mongo:27017")
db = client.sg

@app.route("/", methods=["POST"])
def main():
    rjson = request.json
    if not rjson or rjson.get("model") is None:
        return "", 201
    
    handle(rjson)
    return "", 201


if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", default=4000))    