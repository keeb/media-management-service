#!/bin/bash

export MONGO_HOST=10.0.0.12
export MONGO_PORT=27017
export MONGO_USERNAME=treehouse
export MONGO_PASSWORD=mongo
export MONGO_DATABASE=media

echo "MongoDB environment variables set:"
echo "MONGO_HOST=$MONGO_HOST"
echo "MONGO_PORT=$MONGO_PORT"
echo "MONGO_USERNAME=$MONGO_USERNAME"
echo "MONGO_PASSWORD=$MONGO_PASSWORD"
echo "MONGO_DATABASE=$MONGO_DATABASE"

echo "Running media job worker..."
python media_job_worker.py