#!/usr/bin/env sh

while true
do
    python worker.py || exit
    test -f signal && echo "signal found" && exit
done
