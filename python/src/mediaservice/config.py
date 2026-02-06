"""
Centralized configuration for the media management service.

All configuration is read from environment variables with sensible defaults.
"""

import os
from pathlib import Path


# MongoDB
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "treehouse")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "mongo")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "media")

# SG pipeline uses a separate database
MONGO_SG_DATABASE = os.getenv("MONGO_SG_DATABASE", "sg")

# Media indexer uses its own database
MONGO_INDEXER_DATABASE = os.getenv("MONGO_INDEXER_DATABASE", "media_management")

# File paths
STAGING_DIRECTORY = Path(os.getenv("STAGING_DIRECTORY", "/home/keeb/media/video/staging/"))
DEBUG_LOG_DIRECTORY = Path(os.getenv("DEBUG_LOG_DIRECTORY", "/home/keeb/media/debug/llm-responses/"))

# Download directories for checking existing episodes
ANIME_DIRS = [
    "/home/keeb/media/video/anime/completed",
    "/home/keeb/media/video/anime",
    "/home/keeb/media/video/staging",
    "/home/keeb/media/video/movies",
]

# Transmission RPC
TRANSMISSION_URL = os.getenv("TRANSMISSION_URL", "http://100.71.2.30:9091/transmission/rpc")

# Magnet download endpoint (Flask intermediary)
MAGNET_ENDPOINT = os.getenv("MAGNET_ENDPOINT", "http://hancock:9200/magnet")

# Prompts
PROMPTS_DIR = os.getenv("PROMPTS_DIR", "prompts")

# LLM
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "qwen3:14b")
