import unittest

from hydrowebnext_utils import get_name_from_hydrowebnext_filename


class TestHydrowebnextFilename(unittest.TestCase):
    def test_river_station(self):
        s = get_name_from_hydrowebnext_filename("hydroprd_R_NIGER_ALIBORI_KM1495_exp.txt")
        self.assertEqual(s, "R_NIGER_ALIBORI_KM1495")

    def test_lake_station(self):
        s = get_name_from_hydrowebnext_filename("hydroprd_L_lagdo.txt")
        self.assertEqual(s, "L_lagdo")


if __name__ == '__main__':
    unittest.main()
