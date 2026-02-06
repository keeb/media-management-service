"""
Centralized MongoDB connection factory.

All MongoDB connections in the application should go through this module.
"""

import logging

from pymongo import MongoClient
from pymongo.database import Database

from mediaservice.config import (
    MONGO_HOST,
    MONGO_PORT,
    MONGO_USERNAME,
    MONGO_PASSWORD,
    MONGO_DATABASE,
    MONGO_SG_DATABASE,
)

logger = logging.getLogger(__name__)


def connect(database: str = MONGO_DATABASE, timeout_ms: int = 5000) -> Database:
    """Connect to MongoDB and return a database handle.

    Args:
        database: Database name to connect to.
        timeout_ms: Server selection timeout in milliseconds.

    Returns:
        pymongo Database object.

    Raises:
        ConnectionError: If the connection cannot be established.
    """
    try:
        connection_string = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=timeout_ms)
        client.server_info()
        logger.info(f"Connected to MongoDB at {MONGO_HOST}:{MONGO_PORT}/{database}")
        return client[database]
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise ConnectionError(f"Could not connect to MongoDB: {e}") from e


def get_sg_db() -> Database:
    """Get a database handle for the SuicideGirls pipeline."""
    return connect(database=MONGO_SG_DATABASE)


def get_pending_queue():
    """Get the SG pending queue collection."""
    return get_sg_db().pending


def get_completed_jobs():
    """Get the SG completed jobs collection."""
    return get_sg_db().completed
