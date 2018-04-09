import unittest

from foo.bar2 import increment_sample


class Bar2Test(unittest.TestCase):

    def test_increment_sample(self):
        value = increment_sample()
        self.assertEqual(value, 2.)


if __name__ == '__main__':
    unittest.main()