"""
Jellyfin API client for querying media library inventory.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import requests

from mediaservice.config import JELLYFIN_URL, JELLYFIN_API_KEY

logger = logging.getLogger(__name__)


@dataclass
class LibraryCounts:
    name: str
    library_id: str
    series_count: int = 0
    episode_count: int = 0
    movie_count: int = 0


@dataclass
class InventoryReport:
    libraries: list[LibraryCounts] = field(default_factory=list)

    def _libs_matching(self, *keywords: str) -> list[LibraryCounts]:
        return [
            lib for lib in self.libraries
            if any(kw in lib.name.lower() for kw in keywords)
        ]

    @property
    def anime_titles(self) -> int:
        return sum(lib.series_count for lib in self._libs_matching("anime", "weeb"))

    @property
    def anime_episodes(self) -> int:
        return sum(lib.episode_count for lib in self._libs_matching("anime", "weeb"))

    @property
    def movie_titles(self) -> int:
        return sum(lib.movie_count for lib in self._libs_matching("movies"))

    @property
    def show_titles(self) -> int:
        return sum(lib.series_count for lib in self._libs_matching("shows", "tv", "chinese"))

    @property
    def show_episodes(self) -> int:
        return sum(lib.episode_count for lib in self._libs_matching("shows", "tv", "chinese"))


@dataclass
class ResumeItem:
    series_name: str
    episode_name: str
    season: int
    episode: int
    played_percentage: float
    media_type: str


@dataclass
class ActivityReport:
    episodes_watched_7d: int = 0
    episodes_watched_30d: int = 0
    total_played: int = 0
    continue_watching: list[ResumeItem] = field(default_factory=list)


def _headers(api_key: str) -> dict:
    return {"X-Emby-Token": api_key}


def get_libraries(url: str = JELLYFIN_URL, api_key: str = JELLYFIN_API_KEY) -> list[dict]:
    """Fetch virtual folder (library) list from Jellyfin."""
    resp = requests.get(f"{url}/Library/VirtualFolders", headers=_headers(api_key))
    resp.raise_for_status()
    return resp.json()


def get_item_count(
    library_id: str,
    item_type: str,
    url: str = JELLYFIN_URL,
    api_key: str = JELLYFIN_API_KEY,
) -> int:
    """Return TotalRecordCount for a given item type within a library."""
    resp = requests.get(
        f"{url}/Items",
        headers=_headers(api_key),
        params={
            "ParentId": library_id,
            "IncludeItemTypes": item_type,
            "Recursive": "true",
            "Limit": "0",
        },
    )
    resp.raise_for_status()
    return resp.json().get("TotalRecordCount", 0)


def scan_inventory(
    url: str = JELLYFIN_URL,
    api_key: str = JELLYFIN_API_KEY,
) -> InventoryReport:
    """Query all Jellyfin libraries and return an InventoryReport."""
    libs = get_libraries(url, api_key)
    report = InventoryReport()

    for lib in libs:
        name = lib.get("Name", "")
        lib_id = lib.get("ItemId", "")
        collection_type = lib.get("CollectionType", "")
        logger.info(f"Scanning library: {name} ({collection_type})")

        counts = LibraryCounts(name=name, library_id=lib_id)

        if collection_type in ("tvshows",):
            counts.series_count = get_item_count(lib_id, "Series", url, api_key)
            counts.episode_count = get_item_count(lib_id, "Episode", url, api_key)
        elif collection_type in ("movies",):
            counts.movie_count = get_item_count(lib_id, "Movie", url, api_key)

        report.libraries.append(counts)

    return report


def _get_first_user_id(url: str, api_key: str) -> str:
    """Return the first user's ID from the Jellyfin server."""
    resp = requests.get(f"{url}/Users", headers=_headers(api_key))
    resp.raise_for_status()
    users = resp.json()
    if not users:
        raise ValueError("No users found on Jellyfin server")
    return users[0]["Id"]


def _count_played_since(
    user_id: str,
    since: datetime,
    url: str,
    api_key: str,
) -> int:
    """Count episodes played since a given datetime by paginating through results."""
    count = 0
    start_index = 0
    batch_size = 200

    while True:
        resp = requests.get(
            f"{url}/Users/{user_id}/Items",
            headers=_headers(api_key),
            params={
                "SortBy": "DatePlayed",
                "SortOrder": "Descending",
                "Filters": "IsPlayed",
                "IncludeItemTypes": "Episode",
                "Recursive": "true",
                "Limit": str(batch_size),
                "StartIndex": str(start_index),
            },
        )
        resp.raise_for_status()
        items = resp.json().get("Items", [])
        if not items:
            break

        for item in items:
            played = item.get("UserData", {}).get("LastPlayedDate", "")
            if not played:
                continue
            played_dt = datetime.fromisoformat(played.replace("Z", "+00:00"))
            if played_dt >= since:
                count += 1
            else:
                return count

        start_index += batch_size

    return count


def scan_activity(
    url: str = JELLYFIN_URL,
    api_key: str = JELLYFIN_API_KEY,
    user_id: str | None = None,
) -> ActivityReport:
    """Query Jellyfin for watch activity data."""
    if user_id is None:
        user_id = _get_first_user_id(url, api_key)

    now = datetime.now(timezone.utc)
    report = ActivityReport()

    # Total played episodes
    resp = requests.get(
        f"{url}/Users/{user_id}/Items",
        headers=_headers(api_key),
        params={
            "Filters": "IsPlayed",
            "IncludeItemTypes": "Episode",
            "Recursive": "true",
            "Limit": "0",
        },
    )
    resp.raise_for_status()
    report.total_played = resp.json().get("TotalRecordCount", 0)

    # Episodes watched in last 7 and 30 days
    report.episodes_watched_7d = _count_played_since(
        user_id, now - timedelta(days=7), url, api_key,
    )
    report.episodes_watched_30d = _count_played_since(
        user_id, now - timedelta(days=30), url, api_key,
    )

    # Continue watching (resume) items
    resp = requests.get(
        f"{url}/Users/{user_id}/Items/Resume",
        headers=_headers(api_key),
        params={"Limit": "10", "Fields": "SeriesName"},
    )
    resp.raise_for_status()
    for item in resp.json().get("Items", []):
        report.continue_watching.append(ResumeItem(
            series_name=item.get("SeriesName", item.get("Name", "")),
            episode_name=item.get("Name", ""),
            season=item.get("ParentIndexNumber", 0),
            episode=item.get("IndexNumber", 0),
            played_percentage=item.get("UserData", {}).get("PlayedPercentage", 0),
            media_type=item.get("Type", ""),
        ))

    return report
