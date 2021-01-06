# cython: language_level=3
import unittest
import os
from ex2 import IMGOP, IMG0_NAME


class TestStringMethods(unittest.TestCase):
    @unittest.expectedFailure
    def test_NonExistent(self):
        hill0= IMGOP('/noneexistnt/')
        hill0.read_img()

    def test_crop(self):
        hill0= IMGOP(IMG0_NAME)
        hill0.read_img()

        hill0.x0, hill0.y0 = 0, 0
        hill0.x1, hill0.y1 = 10, 10
        hill0.crop()
        self.assertEqual(hill0.roi.shape, (10, 10, 3))



if __name__ == '__main__':
    unittest.main()
