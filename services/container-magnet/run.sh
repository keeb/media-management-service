#!/usr/bin/env sh

docker build -t keeb/container-magnet .

docker run --rm -it \
    --name debug \
    keeb/container-magnet \
    /bin/sh -c "python -i download.py"