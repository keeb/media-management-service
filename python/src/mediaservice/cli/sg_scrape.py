#!/usr/bin/env python3
"""
CLI tool to run the SuicideGirls scrape API server.

This Flask API receives scrape payloads and enqueues them for the worker to process.
"""

import os

import click
from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient


# Initialize MongoDB connection
def get_mongo_client():
    """Get MongoDB client from environment or defaults."""
    host = os.environ.get("MONGO_HOST", "localhost")
    port = os.environ.get("MONGO_PORT", "27017")
    username = os.environ.get("MONGO_USERNAME", "treehouse")
    password = os.environ.get("MONGO_PASSWORD", "mongo")
    return MongoClient(f"mongodb://{username}:{password}@{host}:{port}")


def construct_key(model_name: str, album_name: str) -> dict:
    """Create lookup key for checking duplicates."""
    return {"model": model_name, "album": album_name}


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    CORS(app)

    client = get_mongo_client()
    db = client.sg

    def get_pending_queue():
        return db.pending

    def get_completed_jobs():
        return db.completed

    def save(payload):
        """Save payload to pending queue if not already processed."""
        model_name = payload.get("model")
        album_name = payload.get("album")
        queue = get_pending_queue()
        completed = get_completed_jobs()

        print("looking to see if this payload is already enqueued")
        key = construct_key(model_name, album_name)

        pending = queue.find_one(key)
        if pending is not None:
            print("found in pending")
            return

        done = completed.find_one(key)
        if done is not None:
            print("found in completed")
            return

        print("it isn't. adding")
        queue.insert_one(payload)

    def handle(payload):
        """Handle incoming scrape payload."""
        model_name = payload.get("model")
        album_name = payload.get("album")
        image_list = payload.get("images", [])
        socials_list = payload.get("socials", [])

        print("received model: %s" % model_name)
        print("received album: %s" % album_name)
        print("received number of images %s" % len(image_list))
        print("received number of socials %s" % len(socials_list))

        save(payload)

    @app.route("/", methods=["POST"])
    def main_route():
        rjson = request.json
        if not rjson or rjson.get("model") is None:
            return "", 201

        handle(rjson)
        return "", 201

    @app.route("/health", methods=["GET"])
    def health():
        return "OK", 200

    return app


@click.command("scrape")
@click.option("--port", default=4000, help="Port to run the server on")
@click.option("--debug", is_flag=True, help="Run in debug mode")
def sg_scrape_cmd(port: int, debug: bool):
    """Run the SG scrape API server."""
    if port == 4000:
        port = int(os.environ.get("PORT", 4000))
    if not debug:
        debug = os.environ.get("DEBUG", "false").lower() == "true"

    click.echo(f"Starting SG Scrape API on port {port}")

    app = create_app()
    app.run(debug=debug, host="0.0.0.0", port=port)


def main():
    """Legacy entry point for SG scrape API."""
    sg_scrape_cmd()


if __name__ == "__main__":
    main()
