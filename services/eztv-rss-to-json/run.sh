#!/usr/bin/env sh
PORT=$(docker port ingest | cut -d" " -f3 | cut -d":" -f2 | head -n1)

if [ -z "$PORT" ]; then
    echo "Ingest not running"
    exit 1
fi

echo -ne "Ingest running on port: "
echo $PORT
BASEDIR="/storage/02/code/projects/eztv-rss-to-json/"
cd $BASEDIR

DATA=$(./eztv-rss-to-json)


if [ -z "$DATA" ]; then
    exit 0
fi

curl -X POST -H "Content-Type: application/json" -d "$DATA" http://localhost:$PORT/ingest/json