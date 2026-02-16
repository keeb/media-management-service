import unittest
from unittest.mock import patch, MagicMock

from mediaservice.sources.jellyfin import (
    get_libraries,
    get_item_count,
    scan_inventory,
    InventoryReport,
    LibraryCounts,
)


MOCK_LIBRARIES = [
    {"Name": "weeb shit", "ItemId": "aaa", "CollectionType": "tvshows"},
    {"Name": "Movies", "ItemId": "bbb", "CollectionType": "movies"},
    {"Name": "Shows", "ItemId": "ccc", "CollectionType": "tvshows"},
]


def mock_items_response(total):
    resp = MagicMock()
    resp.json.return_value = {"TotalRecordCount": total}
    resp.raise_for_status = MagicMock()
    return resp


class TestGetLibraries(unittest.TestCase):
    @patch("mediaservice.sources.jellyfin.requests.get")
    def test_returns_library_list(self, mock_get):
        resp = MagicMock()
        resp.json.return_value = MOCK_LIBRARIES
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp

        result = get_libraries("http://test:8096", "fake-key")
        self.assertEqual(len(result), 3)
        mock_get.assert_called_once_with(
            "http://test:8096/Library/VirtualFolders",
            headers={"X-Emby-Token": "fake-key"},
        )

    @patch("mediaservice.sources.jellyfin.requests.get")
    def test_auth_failure_raises(self, mock_get):
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_get.return_value = resp

        with self.assertRaises(Exception):
            get_libraries("http://test:8096", "bad-key")


class TestGetItemCount(unittest.TestCase):
    @patch("mediaservice.sources.jellyfin.requests.get")
    def test_returns_count(self, mock_get):
        mock_get.return_value = mock_items_response(42)

        count = get_item_count("aaa", "Series", "http://test:8096", "fake-key")
        self.assertEqual(count, 42)

        mock_get.assert_called_once_with(
            "http://test:8096/Items",
            headers={"X-Emby-Token": "fake-key"},
            params={
                "ParentId": "aaa",
                "IncludeItemTypes": "Series",
                "Recursive": "true",
                "Limit": "0",
            },
        )


class TestInventoryReport(unittest.TestCase):
    def _make_report(self):
        return InventoryReport(libraries=[
            LibraryCounts(name="weeb shit", library_id="aaa", series_count=50, episode_count=1200),
            LibraryCounts(name="Movies", library_id="bbb", movie_count=300),
            LibraryCounts(name="Shows", library_id="ccc", series_count=25, episode_count=800),
            LibraryCounts(name="chinese", library_id="ddd", series_count=2, episode_count=24),
        ])

    def test_anime_titles(self):
        self.assertEqual(self._make_report().anime_titles, 50)

    def test_anime_episodes(self):
        self.assertEqual(self._make_report().anime_episodes, 1200)

    def test_movie_titles(self):
        self.assertEqual(self._make_report().movie_titles, 300)

    def test_show_titles(self):
        self.assertEqual(self._make_report().show_titles, 27)

    def test_show_episodes(self):
        self.assertEqual(self._make_report().show_episodes, 824)

    def test_empty_report(self):
        report = InventoryReport()
        self.assertEqual(report.anime_titles, 0)
        self.assertEqual(report.movie_titles, 0)
        self.assertEqual(report.show_episodes, 0)


class TestScanInventory(unittest.TestCase):
    @patch("mediaservice.sources.jellyfin.get_item_count")
    @patch("mediaservice.sources.jellyfin.get_libraries")
    def test_builds_report(self, mock_libs, mock_count):
        mock_libs.return_value = MOCK_LIBRARIES

        def count_side_effect(lib_id, item_type, url, api_key):
            counts = {
                ("aaa", "Series"): 50,
                ("aaa", "Episode"): 1200,
                ("bbb", "Movie"): 300,
                ("ccc", "Series"): 25,
                ("ccc", "Episode"): 800,
            }
            return counts.get((lib_id, item_type), 0)

        mock_count.side_effect = count_side_effect

        report = scan_inventory("http://test:8096", "fake-key")
        self.assertEqual(report.anime_titles, 50)
        self.assertEqual(report.anime_episodes, 1200)
        self.assertEqual(report.movie_titles, 300)
        self.assertEqual(report.show_titles, 25)
        self.assertEqual(report.show_episodes, 800)

    @patch("mediaservice.sources.jellyfin.get_libraries")
    def test_connection_failure(self, mock_libs):
        mock_libs.side_effect = ConnectionError("refused")

        with self.assertRaises(ConnectionError):
            scan_inventory("http://bad:8096", "key")


if __name__ == "__main__":
    unittest.main()
