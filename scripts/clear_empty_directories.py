#!/usr/bin/env python

import os
import argparse

arg_parser = argparse.ArgumentParser(description='Clear empty directories')
arg_parser.add_argument('--path', help='Path to the directory to clear', default=os.getcwd())
arg_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
args = arg_parser.parse_args()


list_of_empty_dirs = []

for dir in os.walk(args.path):
    if not os.listdir(dir[0]):
        print(f'Found empty directory: {dir[0]}')
        list_of_empty_dirs.append(dir)


if not args.dry_run:
    for dir in list_of_empty_dirs:
        os.rmdir(dir[0])
        
