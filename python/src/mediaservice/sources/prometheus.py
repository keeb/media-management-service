"""
Prometheus Pushgateway client for pushing media inventory metrics.
"""

import logging
import time

import requests

from mediaservice.config import PUSHGATEWAY_URL

logger = logging.getLogger(__name__)

JOB_NAME = "media_inventory"
ACTIVITY_JOB_NAME = "media_activity"


def _build_metrics_payload(report) -> str:
    """Format an InventoryReport as Prometheus text exposition."""
    lines = [
        f"# HELP mms_inventory_anime_titles Number of anime series titles",
        f"# TYPE mms_inventory_anime_titles gauge",
        f"mms_inventory_anime_titles {report.anime_titles}",
        f"# HELP mms_inventory_anime_episodes Number of anime episodes",
        f"# TYPE mms_inventory_anime_episodes gauge",
        f"mms_inventory_anime_episodes {report.anime_episodes}",
        f"# HELP mms_inventory_movie_titles Number of movie titles",
        f"# TYPE mms_inventory_movie_titles gauge",
        f"mms_inventory_movie_titles {report.movie_titles}",
        f"# HELP mms_inventory_show_titles Number of TV show titles",
        f"# TYPE mms_inventory_show_titles gauge",
        f"mms_inventory_show_titles {report.show_titles}",
        f"# HELP mms_inventory_show_episodes Number of TV show episodes",
        f"# TYPE mms_inventory_show_episodes gauge",
        f"mms_inventory_show_episodes {report.show_episodes}",
        f"# HELP mms_inventory_last_scan_timestamp Unix timestamp of last scan",
        f"# TYPE mms_inventory_last_scan_timestamp gauge",
        f"mms_inventory_last_scan_timestamp {int(time.time())}",
        "",
    ]
    return "\n".join(lines)


def _build_activity_payload(activity) -> str:
    """Format an ActivityReport as Prometheus text exposition."""
    lines = [
        "# HELP mms_activity_episodes_watched_7d Episodes watched in last 7 days",
        "# TYPE mms_activity_episodes_watched_7d gauge",
        f"mms_activity_episodes_watched_7d {activity.episodes_watched_7d}",
        "# HELP mms_activity_episodes_watched_30d Episodes watched in last 30 days",
        "# TYPE mms_activity_episodes_watched_30d gauge",
        f"mms_activity_episodes_watched_30d {activity.episodes_watched_30d}",
        "# HELP mms_activity_total_played Total episodes ever played",
        "# TYPE mms_activity_total_played gauge",
        f"mms_activity_total_played {activity.total_played}",
        "# HELP mms_activity_continue_watching Number of in-progress items",
        "# TYPE mms_activity_continue_watching gauge",
        f"mms_activity_continue_watching {len(activity.continue_watching)}",
        "# HELP mms_activity_resume_item In-progress item with watch percentage",
        "# TYPE mms_activity_resume_item gauge",
    ]
    for item in activity.continue_watching:
        series = item.series_name.replace('"', '\\"')
        episode = item.episode_name.replace('"', '\\"')
        label = f'series="{series}",episode="S{item.season}E{item.episode} {episode}"'
        lines.append(f"mms_activity_resume_item{{{label}}} {item.played_percentage:.0f}")
    lines.append("")
    return "\n".join(lines)


def _push(payload: str, job: str, pushgateway_url: str) -> None:
    """Push a metrics payload to Pushgateway."""
    url = f"{pushgateway_url}/metrics/job/{job}"
    logger.info(f"Pushing metrics to {url}")
    resp = requests.put(
        url,
        data=payload,
        headers={"Content-Type": "text/plain"},
    )
    resp.raise_for_status()
    logger.info("Metrics pushed successfully")


def push_inventory_metrics(report, pushgateway_url: str = PUSHGATEWAY_URL) -> None:
    """Push inventory metrics to Prometheus Pushgateway."""
    payload = _build_metrics_payload(report)
    _push(payload, JOB_NAME, pushgateway_url)


def push_activity_metrics(activity, pushgateway_url: str = PUSHGATEWAY_URL) -> None:
    """Push watch activity metrics to Prometheus Pushgateway."""
    payload = _build_activity_payload(activity)
    _push(payload, ACTIVITY_JOB_NAME, pushgateway_url)
