"""
Shared magnet link download utility.

Posts magnet URIs to a download endpoint (e.g., the Flask intermediary at hancock:9200).
"""

import json
import logging

import requests

from mediaservice.config import MAGNET_ENDPOINT

logger = logging.getLogger(__name__)


def download_magnets(
    magnets: list[str],
    endpoint: str = MAGNET_ENDPOINT,
) -> None:
    """Send magnet links to the download endpoint.

    Args:
        magnets: List of magnet URI strings.
        endpoint: URL to POST magnet links to.
    """
    header = {"Content-type": "application/json"}
    for magnet in magnets:
        logger.info(f"Sending magnet to {endpoint}")
        data = {"magnet": magnet}
        response = requests.post(endpoint, data=json.dumps(data), headers=header, timeout=30)
        logger.info(f"Response: {response.text}")
