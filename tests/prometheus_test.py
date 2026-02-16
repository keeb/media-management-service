import unittest
from unittest.mock import patch, MagicMock

from mediaservice.sources.jellyfin import InventoryReport, LibraryCounts
from mediaservice.sources.prometheus import _build_metrics_payload, push_inventory_metrics


class TestBuildMetricsPayload(unittest.TestCase):
    def setUp(self):
        self.report = InventoryReport(libraries=[
            LibraryCounts(name="weeb shit", library_id="aaa", series_count=50, episode_count=1200),
            LibraryCounts(name="Movies", library_id="bbb", movie_count=300),
            LibraryCounts(name="Shows", library_id="ccc", series_count=25, episode_count=800),
        ])

    def test_contains_all_metrics(self):
        payload = _build_metrics_payload(self.report)
        self.assertIn("mms_inventory_anime_titles 50", payload)
        self.assertIn("mms_inventory_anime_episodes 1200", payload)
        self.assertIn("mms_inventory_movie_titles 300", payload)
        self.assertIn("mms_inventory_show_titles 25", payload)
        self.assertIn("mms_inventory_show_episodes 800", payload)
        self.assertIn("mms_inventory_last_scan_timestamp", payload)

    def test_has_type_annotations(self):
        payload = _build_metrics_payload(self.report)
        self.assertIn("# TYPE mms_inventory_anime_titles gauge", payload)
        self.assertIn("# TYPE mms_inventory_last_scan_timestamp gauge", payload)

    def test_has_help_annotations(self):
        payload = _build_metrics_payload(self.report)
        self.assertIn("# HELP mms_inventory_anime_titles", payload)


class TestPushInventoryMetrics(unittest.TestCase):
    @patch("mediaservice.sources.prometheus.requests.put")
    def test_puts_to_correct_url(self, mock_put):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        mock_put.return_value = resp

        report = InventoryReport(libraries=[
            LibraryCounts(name="Anime", library_id="a", series_count=10, episode_count=100),
        ])

        push_inventory_metrics(report, pushgateway_url="http://push:9091")

        mock_put.assert_called_once()
        call_args = mock_put.call_args
        self.assertEqual(call_args[0][0], "http://push:9091/metrics/job/media_inventory")
        self.assertEqual(call_args[1]["headers"]["Content-Type"], "text/plain")
        self.assertIn("mms_inventory_anime_titles 10", call_args[1]["data"])

    @patch("mediaservice.sources.prometheus.requests.put")
    def test_raises_on_failure(self, mock_put):
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("500")
        mock_put.return_value = resp

        report = InventoryReport()
        with self.assertRaises(Exception):
            push_inventory_metrics(report, pushgateway_url="http://push:9091")


if __name__ == "__main__":
    unittest.main()
