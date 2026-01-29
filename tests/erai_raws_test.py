import unittest
from mediaservice.sources.erai_raws import (
    parse_title,
    BATCH_PATTERN,
    Episode,
    filter_batch,
    filter_by_resolution,
    filter_to_configured_seasons,
    parse_subtitle,
    find_season_by_subtitle,
    resolve_season_episode,
)


class TestTitleParsing(unittest.TestCase):
    def test_parse_standard_title(self):
        title = "[Erai-raws] Dragon Raja II - 16 (JA) [1080p CR WEBRip HEVC AAC]"
        result = parse_title(title)

        self.assertIsNotNone(result)
        self.assertEqual(result["show_name"], "Dragon Raja II")
        self.assertEqual(result["episode"], "16")
        self.assertEqual(result["language"], "JA")
        self.assertEqual(result["resolution"], "1080p")

    def test_parse_title_without_language(self):
        title = "[Erai-raws] Jujutsu Kaisen - 45 [1080p][Multiple Subtitle]"
        result = parse_title(title)

        self.assertIsNotNone(result)
        self.assertEqual(result["show_name"], "Jujutsu Kaisen")
        self.assertEqual(result["episode"], "45")
        self.assertIsNone(result["language"])
        self.assertEqual(result["resolution"], "1080p")

    def test_parse_title_with_version(self):
        title = "[Erai-raws] Oshi no Ko - 23v2 (EN) [1080p CR WEBRip HEVC AAC]"
        result = parse_title(title)

        self.assertIsNotNone(result)
        self.assertEqual(result["show_name"], "Oshi no Ko")
        self.assertEqual(result["episode"], "23v2")
        self.assertEqual(result["language"], "EN")
        self.assertEqual(result["resolution"], "1080p")

    def test_parse_720p_title(self):
        title = "[Erai-raws] Some Anime - 01 [720p][Multiple Subtitle]"
        result = parse_title(title)

        self.assertIsNotNone(result)
        self.assertEqual(result["resolution"], "720p")

    def test_parse_title_with_special_chars(self):
        title = "[Erai-raws] Re:Zero kara Hajimeru Isekai Seikatsu - 50 (JA) [1080p CR WEBRip HEVC AAC]"
        result = parse_title(title)

        self.assertIsNotNone(result)
        self.assertEqual(result["show_name"], "Re:Zero kara Hajimeru Isekai Seikatsu")
        self.assertEqual(result["episode"], "50")

    def test_parse_invalid_title(self):
        title = "Some random torrent name"
        result = parse_title(title)
        self.assertIsNone(result)

    def test_parse_non_erai_raws(self):
        title = "[SubsPlease] Dandadan - 01 (1080p) [ABC123].mkv"
        result = parse_title(title)
        self.assertIsNone(result)


class TestBatchDetection(unittest.TestCase):
    def test_batch_pattern_with_spaces(self):
        title = "[Erai-raws] Show Name - 01 ~ 23 [1080p]"
        self.assertTrue(BATCH_PATTERN.search(title))

    def test_batch_pattern_without_spaces(self):
        title = "[Erai-raws] Show Name - 01~12 [1080p]"
        self.assertTrue(BATCH_PATTERN.search(title))

    def test_single_episode_no_match(self):
        title = "[Erai-raws] Show Name - 16 [1080p]"
        self.assertFalse(BATCH_PATTERN.search(title))


class TestEpisodeDataclass(unittest.TestCase):
    def test_episode_number_without_version(self):
        ep = Episode(
            title="test",
            show_name="Test Show",
            episode="16",
            language="JA",
            resolution="1080p",
            info_hash="abc123",
            seeders=10
        )
        self.assertEqual(ep.episode_number, "16")

    def test_episode_number_with_version(self):
        ep = Episode(
            title="test",
            show_name="Test Show",
            episode="16v2",
            language="JA",
            resolution="1080p",
            info_hash="abc123",
            seeders=10
        )
        self.assertEqual(ep.episode_number, "16")

    def test_episode_padded(self):
        ep = Episode(
            title="test",
            show_name="Test Show",
            episode="5",
            language="JA",
            resolution="1080p",
            info_hash="abc123",
            seeders=10
        )
        self.assertEqual(ep.episode_padded, "05")

    def test_magnet_construction(self):
        ep = Episode(
            title="[Erai-raws] Test - 01 [1080p]",
            show_name="Test",
            episode="01",
            language=None,
            resolution="1080p",
            info_hash="abc123def456",
            seeders=10
        )
        magnet = ep.magnet
        self.assertTrue(magnet.startswith("magnet:?xt=urn:btih:abc123def456"))
        self.assertIn("dn=", magnet)


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.episodes = [
            Episode("t1", "Show", "01", "JA", "1080p", "h1", 10),
            Episode("t2", "Show", "02", "JA", "720p", "h2", 10),
            Episode("t3", "Show", "03", "JA", "1080p", "h3", 10),
            Episode("t4 01 ~ 12", "Show", "01", "JA", "1080p", "h4", 10),
        ]

    def test_filter_by_resolution(self):
        result = filter_by_resolution(self.episodes, "1080p")
        self.assertEqual(len(result), 3)

    def test_filter_batch(self):
        result = filter_batch(self.episodes)
        self.assertEqual(len(result), 3)
        for ep in result:
            self.assertNotIn("~", ep.title)


class TestSeasonResolution(unittest.TestCase):
    def setUp(self):
        self.show_config = {
            "name": "jujutsu kaisen",
            "seasons": [
                {"number": 1, "episodes": [1, 24]},
                {"number": 2, "episodes": [25, 47]},
                {"number": 3, "episodes": [1, 24], "subtitle": "Shimetsu Kaiyuu"},
            ]
        }

    def test_parse_subtitle_with_subtitle(self):
        base, subtitle = parse_subtitle("Jujutsu Kaisen - Shimetsu Kaiyuu")
        self.assertEqual(base, "Jujutsu Kaisen")
        self.assertEqual(subtitle, "Shimetsu Kaiyuu")

    def test_parse_subtitle_no_subtitle(self):
        base, subtitle = parse_subtitle("Jujutsu Kaisen")
        self.assertEqual(base, "Jujutsu Kaisen")
        self.assertIsNone(subtitle)

    def test_parse_subtitle_with_episode_separator(self):
        # Should not match episode separators like " - 01"
        base, subtitle = parse_subtitle("Jujutsu Kaisen - Shimetsu Kaiyuu - Zenpen")
        self.assertEqual(base, "Jujutsu Kaisen")
        self.assertEqual(subtitle, "Shimetsu Kaiyuu")

    def test_find_season_by_subtitle_match(self):
        season = find_season_by_subtitle("Shimetsu Kaiyuu", self.show_config)
        self.assertEqual(season, 3)

    def test_find_season_by_subtitle_no_match(self):
        season = find_season_by_subtitle("Unknown Season", self.show_config)
        self.assertIsNone(season)

    def test_find_season_by_subtitle_case_insensitive(self):
        season = find_season_by_subtitle("shimetsu kaiyuu", self.show_config)
        self.assertEqual(season, 3)

    def test_resolve_season_episode_season1(self):
        season, ep = resolve_season_episode(1, self.show_config)
        self.assertEqual(season, 1)
        self.assertEqual(ep, 1)

        season, ep = resolve_season_episode(24, self.show_config)
        self.assertEqual(season, 1)
        self.assertEqual(ep, 24)

    def test_resolve_season_episode_season2(self):
        season, ep = resolve_season_episode(25, self.show_config)
        self.assertEqual(season, 2)
        self.assertEqual(ep, 1)

        season, ep = resolve_season_episode(45, self.show_config)
        self.assertEqual(season, 2)
        self.assertEqual(ep, 21)

        season, ep = resolve_season_episode(47, self.show_config)
        self.assertEqual(season, 2)
        self.assertEqual(ep, 23)

    def test_resolve_season_episode_no_match(self):
        # Episode outside any configured range
        season, ep = resolve_season_episode(100, self.show_config)
        self.assertIsNone(season)
        self.assertEqual(ep, 100)

    def test_resolve_season_episode_no_config(self):
        season, ep = resolve_season_episode(5, {})
        self.assertIsNone(season)
        self.assertEqual(ep, 5)


class TestFilterToConfiguredSeasons(unittest.TestCase):
    def setUp(self):
        self.show_config = {
            "name": "jujutsu kaisen",
            "seasons": [
                {"number": 1, "episodes": [1, 24]},
                {"number": 2, "episodes": [25, 47]},
                {"number": 3, "episodes": [1, 24], "subtitle": "Shimetsu Kaiyuu"},
            ]
        }

    def test_filter_to_configured_seasons_with_subtitle(self):
        """Only episodes matching configured subtitles are kept."""
        episodes = [
            Episode("t1", "Jujutsu Kaisen - Shimetsu Kaiyuu", "05", "JA", "1080p", "h1", 10),
            Episode("t2", "Jujutsu Kaisen 2nd Season", "21", "JA", "1080p", "h2", 10),
            Episode("t3", "Jujutsu Kaisen - Shimetsu Kaiyuu - Zenpen", "06", "JA", "1080p", "h3", 10),
            Episode("t4", "Jujutsu Kaisen", "45", "JA", "1080p", "h4", 10),
        ]
        result = filter_to_configured_seasons(episodes, self.show_config)
        # Only episodes 1 and 3 have the configured subtitle "Shimetsu Kaiyuu"
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].episode, "05")
        self.assertEqual(result[1].episode, "06")

    def test_filter_to_configured_seasons_no_config(self):
        """All episodes kept when no config provided."""
        episodes = [
            Episode("t1", "Jujutsu Kaisen - Shimetsu Kaiyuu", "05", "JA", "1080p", "h1", 10),
            Episode("t2", "Jujutsu Kaisen 2nd Season", "21", "JA", "1080p", "h2", 10),
        ]
        result = filter_to_configured_seasons(episodes, None)
        self.assertEqual(len(result), 2)

    def test_filter_to_configured_seasons_empty_config(self):
        """All episodes kept when config has no seasons."""
        episodes = [
            Episode("t1", "Some Show", "01", "JA", "1080p", "h1", 10),
        ]
        result = filter_to_configured_seasons(episodes, {})
        self.assertEqual(len(result), 1)

    def test_filter_to_configured_seasons_no_subtitles_in_config(self):
        """All episodes kept when config has no subtitle seasons."""
        config = {
            "name": "some show",
            "seasons": [
                {"number": 1, "episodes": [1, 24]},
                {"number": 2, "episodes": [25, 48]},
            ]
        }
        episodes = [
            Episode("t1", "Some Show", "01", "JA", "1080p", "h1", 10),
            Episode("t2", "Some Show", "25", "JA", "1080p", "h2", 10),
        ]
        result = filter_to_configured_seasons(episodes, config)
        self.assertEqual(len(result), 2)

    def test_filter_to_configured_seasons_case_insensitive(self):
        """Subtitle matching is case insensitive."""
        episodes = [
            Episode("t1", "Jujutsu Kaisen - SHIMETSU KAIYUU", "05", "JA", "1080p", "h1", 10),
        ]
        result = filter_to_configured_seasons(episodes, self.show_config)
        self.assertEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()
