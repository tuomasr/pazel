"""Test generating Bazel rules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

from pazel.generate_rule import sort_module_names


class TestGenerateRule(unittest.TestCase):
    """Test generating Bazel rules."""

    def test_sort_module_names(self):
        """Test sort_module_names."""
        modules = ["abc", "xyz", "foo.bar1", "foo.bar2", "foo.abc.abc", "foo.cba.cba"]
        sorted_modules = sort_module_names(modules)

        expected_sorted_modules = ["abc", "xyz", "foo.bar1", "foo.bar2", "foo.abc.abc",
                                   "foo.cba.cba"]

        self.assertEqual(sorted_modules, expected_sorted_modules)


if __name__ == '__main__':
    unittest.main()
