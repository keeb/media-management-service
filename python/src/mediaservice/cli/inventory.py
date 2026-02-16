"""
CLI command for scanning Jellyfin media library inventory.
"""

import json
import logging

import click

from mediaservice.config import JELLYFIN_URL, JELLYFIN_API_KEY, JELLYFIN_USER_ID, PUSHGATEWAY_URL

logger = logging.getLogger(__name__)


@click.group("inventory")
def inventory_cmd():
    """Media library inventory tools."""
    pass


@inventory_cmd.command()
@click.option("--json-output", "as_json", is_flag=True, help="Output as JSON")
@click.option("--push-metrics", is_flag=True, help="Push metrics to Prometheus Pushgateway")
@click.option("--jellyfin-url", default=JELLYFIN_URL, help="Jellyfin server URL")
@click.option("--api-key", default=JELLYFIN_API_KEY, help="Jellyfin API key")
@click.option("--pushgateway-url", default=PUSHGATEWAY_URL, help="Pushgateway URL")
@click.option("--user-id", default=JELLYFIN_USER_ID or None, help="Jellyfin user ID for activity (default: first user)")
def scan(as_json, push_metrics, jellyfin_url, api_key, pushgateway_url, user_id):
    """Scan Jellyfin libraries and report inventory counts."""
    from mediaservice.sources.jellyfin import scan_inventory, scan_activity
    from mediaservice.sources.prometheus import push_inventory_metrics, push_activity_metrics

    if not api_key:
        raise click.ClickException("Jellyfin API key required (--api-key or JELLYFIN_API_KEY env var)")

    report = scan_inventory(url=jellyfin_url, api_key=api_key)
    activity = scan_activity(url=jellyfin_url, api_key=api_key, user_id=user_id)

    if as_json:
        data = {
            "anime_titles": report.anime_titles,
            "anime_episodes": report.anime_episodes,
            "movie_titles": report.movie_titles,
            "show_titles": report.show_titles,
            "show_episodes": report.show_episodes,
            "libraries": [
                {
                    "name": lib.name,
                    "library_id": lib.library_id,
                    "series_count": lib.series_count,
                    "episode_count": lib.episode_count,
                    "movie_count": lib.movie_count,
                }
                for lib in report.libraries
            ],
            "activity": {
                "episodes_watched_7d": activity.episodes_watched_7d,
                "episodes_watched_30d": activity.episodes_watched_30d,
                "total_played": activity.total_played,
                "continue_watching": [
                    {
                        "series": item.series_name,
                        "episode": f"S{item.season}E{item.episode}",
                        "name": item.episode_name,
                        "progress": round(item.played_percentage),
                    }
                    for item in activity.continue_watching
                ],
            },
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo("Media Library Inventory")
        click.echo("=" * 40)
        for lib in report.libraries:
            click.echo(f"\n  {lib.name}")
            if lib.series_count:
                click.echo(f"    Series:   {lib.series_count}")
            if lib.episode_count:
                click.echo(f"    Episodes: {lib.episode_count}")
            if lib.movie_count:
                click.echo(f"    Movies:   {lib.movie_count}")
        click.echo("\n" + "-" * 40)
        click.echo(f"  Anime:  {report.anime_titles} titles, {report.anime_episodes} episodes")
        click.echo(f"  Movies: {report.movie_titles} titles")
        click.echo(f"  Shows:  {report.show_titles} titles, {report.show_episodes} episodes")

        click.echo("\nWatch Activity")
        click.echo("=" * 40)
        click.echo(f"  Last 7 days:  {activity.episodes_watched_7d} episodes")
        click.echo(f"  Last 30 days: {activity.episodes_watched_30d} episodes")
        click.echo(f"  All time:     {activity.total_played} episodes")
        if activity.continue_watching:
            click.echo("\n  Continue Watching:")
            for item in activity.continue_watching:
                click.echo(f"    {item.series_name} S{item.season}E{item.episode} ({item.played_percentage:.0f}%)")

    if push_metrics:
        push_inventory_metrics(report, pushgateway_url=pushgateway_url)
        push_activity_metrics(activity, pushgateway_url=pushgateway_url)
        if not as_json:
            click.echo(f"\nMetrics pushed to {pushgateway_url}")
