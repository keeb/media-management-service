"""
Erai-raws anime episode search and download utilities.

Fetches RSS from Nyaa filtered to Erai-raws uploads.
"""

import re
import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote, quote_plus
from dataclasses import dataclass
from typing import Optional

from mediaservice.util.file import crawl_for_files, get_file_name
from mediaservice.util.ollama import run_prompt

FILENAME_PROMPT = "prompts/filename-to-json.prompt"


NYAA_RSS_BASE = "https://nyaa.si/?page=rss&u=Erai-raws"
NYAA_NS = {"nyaa": "https://nyaa.si/xmlns/nyaa"}

# Regex for parsing Erai-raws titles
# Example: [Erai-raws] Dragon Raja II - 16 (JA) [1080p CR WEBRip HEVC AAC]
TITLE_PATTERN = re.compile(
    r'\[Erai-raws\]\s+(.+?)\s+-\s+(\d+(?:v\d)?)\s*(?:\(([A-Z]{2})\))?\s*\[(\d+p)'
)

# Batch detection - episode ranges like "01 ~ 23" or "01~23"
BATCH_PATTERN = re.compile(r'\d+\s*~\s*\d+')

# Subtitle pattern - extracts show name and subtitle
# Example: "Jujutsu Kaisen - Shimetsu Kaiyuu - Zenpen" -> ("Jujutsu Kaisen", "Shimetsu Kaiyuu")
SUBTITLE_PATTERN = re.compile(r'^(.+?)\s+-\s+([A-Za-z][A-Za-z\s]+?)(?:\s+-\s+|$)')


@dataclass
class Episode:
    """Parsed episode from RSS feed."""
    title: str
    show_name: str
    episode: str
    language: Optional[str]
    resolution: str
    info_hash: str
    seeders: int

    @property
    def episode_number(self) -> str:
        """Episode number without version suffix (e.g., '16' from '16v2')."""
        return re.sub(r'v\d+$', '', self.episode)

    @property
    def episode_padded(self) -> str:
        """Zero-padded episode number."""
        return self.episode_number.zfill(2)

    @property
    def magnet(self) -> str:
        """Construct magnet URI from info hash."""
        return construct_magnet(self.info_hash, self.title)


def fetch_rss(query: str) -> str:
    """Fetch filtered RSS from Nyaa for Erai-raws.

    Args:
        query: Show name to search for

    Returns:
        Raw RSS XML string
    """
    encoded_query = quote_plus(query)
    url = f"{NYAA_RSS_BASE}&q={encoded_query}"
    print(f"\nFetching RSS: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def parse_title(title: str) -> Optional[dict]:
    """Parse Erai-raws title format.

    Args:
        title: RSS item title

    Returns:
        Dictionary with show_name, episode, language, resolution or None if no match
    """
    match = TITLE_PATTERN.search(title)
    if not match:
        return None

    return {
        "show_name": match.group(1).strip(),
        "episode": match.group(2),
        "language": match.group(3),  # May be None
        "resolution": match.group(4),
    }


def parse_feed(xml_content: str) -> list[Episode]:
    """Parse RSS XML and extract episodes.

    Args:
        xml_content: Raw RSS XML string

    Returns:
        List of Episode objects
    """
    episodes = []
    root = ET.fromstring(xml_content)

    for item in root.findall(".//item"):
        title_elem = item.find("title")
        info_hash_elem = item.find("nyaa:infoHash", NYAA_NS)
        seeders_elem = item.find("nyaa:seeders", NYAA_NS)

        if title_elem is None or info_hash_elem is None:
            continue

        title = title_elem.text
        info_hash = info_hash_elem.text
        seeders = int(seeders_elem.text) if seeders_elem is not None else 0

        parsed = parse_title(title)
        if parsed is None:
            continue

        episodes.append(Episode(
            title=title,
            show_name=parsed["show_name"],
            episode=parsed["episode"],
            language=parsed["language"],
            resolution=parsed["resolution"],
            info_hash=info_hash,
            seeders=seeders,
        ))

    return episodes


def construct_magnet(info_hash: str, title: str) -> str:
    """Build magnet URI from info hash and title.

    Args:
        info_hash: Nyaa info hash
        title: Display name for the torrent

    Returns:
        Magnet URI string
    """
    encoded_title = quote(title)
    return f"magnet:?xt=urn:btih:{info_hash}&dn={encoded_title}"


def filter_by_resolution(episodes: list[Episode], resolution: str = "1080p") -> list[Episode]:
    """Filter episodes to specified resolution.

    Args:
        episodes: List of Episode objects
        resolution: Resolution to filter for (e.g., "1080p")

    Returns:
        Filtered list of episodes
    """
    return [ep for ep in episodes if ep.resolution == resolution]


def filter_by_language(episodes: list[Episode], language: str) -> list[Episode]:
    """Filter episodes to specified language.

    Episodes without a language tag are always included (treated as matching any language).

    Args:
        episodes: List of Episode objects
        language: Language code to filter for (e.g., "EN", "JA")

    Returns:
        Filtered list of episodes
    """
    return [ep for ep in episodes if ep.language is None or ep.language.upper() == language.upper()]


def deduplicate_prefer_hevc(episodes: list[Episode]) -> list[Episode]:
    """Deduplicate episodes by show name and episode number, preferring HEVC over AVC.

    Args:
        episodes: List of Episode objects

    Returns:
        Deduplicated list with one entry per show/episode combination
    """
    by_episode: dict[tuple[str, str], Episode] = {}

    for ep in episodes:
        # Include show name in key to handle different seasons
        key = (ep.show_name, ep.episode_padded)
        if key not in by_episode:
            by_episode[key] = ep
        else:
            # Prefer HEVC over AVC
            current_is_hevc = "HEVC" in by_episode[key].title
            new_is_hevc = "HEVC" in ep.title
            if new_is_hevc and not current_is_hevc:
                by_episode[key] = ep

    return list(by_episode.values())


def filter_to_configured_seasons(
    episodes: list[Episode],
    show_config: Optional[dict] = None,
) -> list[Episode]:
    """Filter episodes to only include those from active seasons.

    Uses LLM to parse each episode title and extract the season number,
    then filters to only keep episodes from seasons that have a 'subtitle'
    defined (indicating they're actively being downloaded).

    Args:
        episodes: List of Episode objects
        show_config: Show configuration dict with seasons list

    Returns:
        Filtered list with only episodes from active seasons
    """
    if not show_config:
        return episodes

    seasons = show_config.get("seasons", [])
    if not seasons:
        return episodes

    # Get season numbers that have subtitles (active seasons to download)
    active_seasons = {s.get("number") for s in seasons if s.get("subtitle")}
    if not active_seasons:
        # No subtitle-based seasons, don't filter
        return episodes

    print(f"Active seasons to download: {sorted(active_seasons)}")

    remaining = []
    for ep in episodes:
        parsed = parse_with_llm(ep.title)
        if parsed and parsed.get("season") in active_seasons:
            remaining.append(ep)
        elif parsed:
            print(f"Excluding season {parsed.get('season')}: {ep.title[:60]}...")

    return remaining


def filter_batch(episodes: list[Episode]) -> list[Episode]:
    """Exclude batch releases (episode ranges).

    Args:
        episodes: List of Episode objects

    Returns:
        List with batch releases removed
    """
    return [ep for ep in episodes if not BATCH_PATTERN.search(ep.title)]


def normalize(s: str) -> str:
    """Normalize string for comparison."""
    return re.sub(r'[^a-z0-9]', '', s.lower())


def normalize_to_dirname(s: str) -> str:
    """Normalize title to directory name format (lowercase, hyphens)."""
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def parse_with_llm(title: str) -> Optional[dict]:
    """Parse episode title using LLM for accurate season/episode detection.

    Args:
        title: RSS item title (e.g., "[Erai-raws] Jujutsu Kaisen 2nd Season - 23 [1080p]")

    Returns:
        Dictionary with title, season, episode or None if parsing fails
    """
    try:
        result = run_prompt(FILENAME_PROMPT, title, model="qwen3:14b")
        # Handle potential markdown code block wrapper
        if result.startswith("```"):
            result = re.sub(r'^```(?:json)?\n?', '', result)
            result = re.sub(r'\n?```$', '', result)
        return json.loads(result)
    except (json.JSONDecodeError, Exception) as e:
        print(f"LLM parse failed for '{title}': {e}")
        return None


def parse_subtitle(show_name: str) -> tuple[str, Optional[str]]:
    """Extract base show name and subtitle from parsed show name.

    Some shows have subtitles in the RSS title that indicate the season,
    e.g., "Jujutsu Kaisen - Shimetsu Kaiyuu" where "Shimetsu Kaiyuu" is the
    subtitle for season 3.

    Args:
        show_name: Parsed show name from RSS title

    Returns:
        Tuple of (base_name, subtitle) where subtitle may be None
    """
    match = SUBTITLE_PATTERN.match(show_name)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return show_name, None


def find_season_by_subtitle(subtitle: str, show_config: dict) -> Optional[int]:
    """Look up season number by subtitle match.

    Args:
        subtitle: The subtitle to match (e.g., "Shimetsu Kaiyuu")
        show_config: Show configuration dict with seasons list

    Returns:
        Season number if found, None otherwise
    """
    seasons = show_config.get("seasons", [])
    normalized_subtitle = normalize(subtitle)

    for season in seasons:
        season_subtitle = season.get("subtitle")
        if season_subtitle and normalize(season_subtitle) == normalized_subtitle:
            return season.get("number")

    return None


def resolve_season_episode(episode_num: int, show_config: dict) -> tuple[Optional[int], int]:
    """Convert absolute episode number to (season, episode) using config.

    Checks if the episode number falls within any configured season's
    absolute episode range.

    Args:
        episode_num: The episode number from RSS (may be absolute)
        show_config: Show configuration dict with seasons list

    Returns:
        Tuple of (season_number, episode_in_season) if found in config,
        or (None, episode_num) if no matching season config
    """
    seasons = show_config.get("seasons", [])

    for season in seasons:
        episodes_range = season.get("episodes")
        if not episodes_range or len(episodes_range) != 2:
            continue

        start, end = episodes_range
        if start <= episode_num <= end:
            # Calculate episode within season
            episode_in_season = episode_num - start + 1
            return season.get("number"), episode_in_season

    return None, episode_num


def filter_exists(
    episodes: list[Episode],
    dirs: list[str],
    show_config: Optional[dict] = None,
) -> list[Episode]:
    """Remove episodes that already exist in directories.

    Uses LLM to parse each episode title to get (title, season, episode),
    then checks the appropriate season directory for existing files.

    Args:
        episodes: List of Episode objects
        dirs: Directories to check for existing files
        show_config: Optional show configuration (unused, kept for API compat)

    Returns:
        List with existing episodes removed
    """
    import os

    remaining = []

    for ep in episodes:
        # Parse with LLM to get accurate season/episode
        parsed = parse_with_llm(ep.title)
        if not parsed:
            print(f"Could not parse: {ep.title}")
            remaining.append(ep)
            continue

        title = parsed.get("title", "")
        season = parsed.get("season")
        episode = parsed.get("episode")

        if not title or episode is None:
            print(f"Missing title/episode in parse result: {parsed}")
            remaining.append(ep)
            continue

        # Normalize title to directory name
        show_dir = normalize_to_dirname(title)
        episode_padded = str(episode).zfill(2)

        # Check each base directory
        exists = False
        normalized_title = normalize(title)

        for base_dir in dirs:
            # Check 1: Organized season directory {base}/{show}/s{season}/
            if season is not None:
                season_path = os.path.join(base_dir, show_dir, f"s{season}")
                if os.path.isdir(season_path):
                    for filename in os.listdir(season_path):
                        if re.search(rf'[\s\-_]0?{episode}[\s\.\[\(v]', filename):
                            exists = True
                            print(f"Episode {episode_padded} exists: {season_path}/{filename}")
                            break

            # Check 2: Flat show directory {base}/{show}/ (no season subdir)
            if not exists:
                show_path = os.path.join(base_dir, show_dir)
                if os.path.isdir(show_path):
                    for filename in os.listdir(show_path):
                        if os.path.isdir(os.path.join(show_path, filename)):
                            continue
                        if re.search(rf'[\s\-_]0?{episode}[\s\.\[\(v]', filename):
                            exists = True
                            print(f"Episode {episode_padded} exists: {show_path}/{filename}")
                            break

            # Check 3: Flat staging directory - match show name + episode in filename
            if not exists and "staging" in base_dir:
                try:
                    for filename in os.listdir(base_dir):
                        if os.path.isdir(os.path.join(base_dir, filename)):
                            continue
                        if normalized_title in normalize(filename):
                            if re.search(rf'[\s\-_]0?{episode}[\s\.\[\(v]', filename):
                                exists = True
                                print(f"Episode {episode_padded} exists: {base_dir}/{filename}")
                                break
                except OSError:
                    pass

            if exists:
                break

        if not exists:
            print(f"Episode {episode_padded} (s{season}) not found locally")
            remaining.append(ep)

    if remaining:
        print(f"\nEpisodes to download: {[ep.episode for ep in remaining]}")
    else:
        print("\nNo new episodes to download")

    return remaining


def download_magnets(
    episodes: list[Episode],
    endpoint: str = "http://hancock:9200/magnet"
) -> None:
    """Send magnet links to download endpoint.

    Args:
        episodes: List of Episode objects
        endpoint: URL to POST magnet links to
    """
    for ep in episodes:
        print(f"Downloading episode {ep.episode}: {ep.title}")

        header = {'Content-type': 'application/json'}
        data = {"magnet": ep.magnet}
        response = requests.post(endpoint, data=json.dumps(data), headers=header, timeout=30)
        print(response.text)


def search_show(
    query: str,
    resolution: str = "1080p",
    language: str = None,
    dirs: list[str] = None,
    filter_existing: bool = True,
    show_config: Optional[dict] = None,
) -> list[Episode]:
    """Search for a show and return filtered episodes.

    Args:
        query: Show name to search for
        resolution: Resolution to filter for
        language: Language code to filter for (e.g., "EN", "JA"), None for no filter
        dirs: Directories to check for existing files
        filter_existing: Whether to filter out existing episodes
        show_config: Optional show configuration with season mappings for
            resolving absolute episode numbers to season/episode pairs

    Returns:
        List of Episode objects ready for download
    """
    if dirs is None:
        dirs = []

    xml = fetch_rss(query)
    episodes = parse_feed(xml)
    print(f"Found {len(episodes)} total items in feed")

    # Filter batch releases
    episodes = filter_batch(episodes)
    print(f"After excluding batches: {len(episodes)}")

    # Filter by resolution
    episodes = filter_by_resolution(episodes, resolution)
    print(f"After filtering to {resolution}: {len(episodes)}")

    # Filter by language
    if language:
        episodes = filter_by_language(episodes, language)
        print(f"After filtering to {language}: {len(episodes)}")

    # Deduplicate preferring HEVC
    episodes = deduplicate_prefer_hevc(episodes)
    print(f"After deduplication (prefer HEVC): {len(episodes)}")

    # Filter to configured seasons (when subtitles are configured)
    if show_config:
        episodes = filter_to_configured_seasons(episodes, show_config)
        print(f"After filtering to configured seasons: {len(episodes)}")

    # Filter existing
    if filter_existing and dirs:
        episodes = filter_exists(episodes, dirs, show_config=show_config)

    return episodes
