#!/bin/bash

# Script to parse media filenames using Ollama with the prompt file
# Usage: ./parse_filename.sh "filename.ext"

if [ $# -eq 0 ]; then
  echo "Usage: $0 \"filename\""
  echo "Example: $0 \"The.Sopranos.S01E01.Pilot.avi\""
  exit 1
fi

filename="$1"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
prompt_file="$script_dir/prompts/filename-to-json.prompt"

if [ ! -f "$prompt_file" ]; then
  echo "Error: Prompt file not found at $prompt_file"
  exit 1
fi

# Use the prompt file and pass the filename as input to Ollama
(
  cat "$prompt_file"
  echo
  echo "$filename"
) | ollama run dolphin3
