#!/bin/bash

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source ../../env/bin/activate
else
    echo "Virtual environment already activated: $VIRTUAL_ENV"
fi

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

echo "Running media job worker until queue is empty..."

while true; do
    echo "Starting worker iteration..."
    
    # Run the worker and capture its output
    python media_job_worker.py
    worker_exit_code=$?
    
    # If worker exits with non-zero code or finds no jobs, stop
    if [ $worker_exit_code -ne 0 ]; then
        echo "Worker exited with error code $worker_exit_code, stopping."
        break
    fi
    
    # Check if the worker found a job by looking at the log output
    # If no job was found, the worker logs "No pending jobs found in queue"
    if python -c "
import os
try:
    from mediaservice.mongo import connect_to_mongo
    db = connect_to_mongo()
    job = db.jobs.find_one({'status': {'\$in': ['pending', 'queued', None]}})
    if job is None:
        print('0')
    else:
        print('1')
except Exception as e:
    print('0')  # Assume no jobs if there's an error
" | grep -q "^0$"; then
        echo "No more jobs in queue, stopping worker."
        break
    fi
    
    echo "More jobs available, continuing..."
    echo "Waiting 5 seconds before next iteration..."
    sleep 5
done

echo "Worker finished - no more jobs in queue."