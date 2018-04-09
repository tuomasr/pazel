import unittest

import requests

from foo.bar1 import sample


class Bar1Test(unittest.TestCase):

    def test_sample(self):
        value = sample()
        self.assertEqual(value, 1.)


if __name__ == '__main__':
    unittest.main()