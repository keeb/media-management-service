import unittest
from mediaservice.organize.parse import parse_tv, parse_anime, is_tv, is_anime


class TestParser(unittest.TestCase):
    def test_parse_tv_show(self):
        show = "The Handmaids Tale S05E10 Safe 1080p HULU WEBRip DD5 1 X 264-EVO [eztv]"

        self.assertTrue(is_tv(show))
        result = parse_tv(show)

        self.assertEqual(result.get("name"), "The Handmaids Tale")

    def test_subsplease_format(self):
        show = "[SubsPlease] Bye Bye, Earth - 01 (1080p) [AED5D744].mkv"
        result = parse_anime(show)
        self.assertEqual(result.get("name"), "Bye Bye, Earth -")
        self.assertEqual(result.get("episode"), "01")


if __name__ == '__main__':
    unittest.main()
