import unittest
from filter import parse

class TestParser(unittest.TestCase):
    def test_parse_complicated_show(self):
        show = "The Handmaids Tale S05E10 Safe 1080p HULU WEBRip DD5 1 X 264-EVO [eztv]"

        result = parse(show)

        self.assertEqual(result.get("name"), "The Handmaids Tale")
        self.assertEqual(result.get("season"), "05")
        self.assertEqual(result.get("episode"), "10")
        self.assertEqual(result.get("resolution"), "1080p")

    def test_subsplease_format(self):
        show = "[SubsPlease] Bye Bye, Earth - 01 (1080p) [AED5D744].mkv"
        result = parse(show)
        print(result)
        self.assertEqual(result.get("name"), "Bye Bye, Earth")
        


if __name__ == '__main__':
    unittest.main()
