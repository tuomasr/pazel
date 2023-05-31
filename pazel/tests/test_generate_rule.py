"""Test generating Bazel rules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

from pazel.generate_rule import sort_module_names
from pazel.generate_rule import translate_dot_module_name_to_bazel


class TestGenerateRule(unittest.TestCase):
    """Test generating Bazel rules."""

    def test_sort_module_names(self):
        """Test sort_module_names."""
        modules = ["abc", "xyz", "foo.bar1", "foo.bar2", "foo.abc.abc", "foo.cba.cba"]
        sorted_modules = sort_module_names(modules)

        expected_sorted_modules = ["abc", "xyz", "foo.bar1", "foo.bar2", "foo.abc.abc",
                                   "foo.cba.cba"]

        self.assertEqual(sorted_modules, expected_sorted_modules)

    def test_translate_dot_module_name_to_bazel(self):
        # Simple paths
        self.assertEqual(translate_dot_module_name_to_bazel("abc"), ":abc")
        self.assertEqual(translate_dot_module_name_to_bazel("abc.xyz"), "//abc:xyz")
        self.assertEqual(translate_dot_module_name_to_bazel("abc.def.xyz"), "//abc/def:xyz")
        self.assertEqual(translate_dot_module_name_to_bazel("abc.def.ghi.xyz"), "//abc/def/ghi:xyz")
        # Rule matches package shorthand
        self.assertEqual(translate_dot_module_name_to_bazel("abc.abc"), "//abc")
        self.assertEqual(translate_dot_module_name_to_bazel("abc.def.def"), "//abc/def")
        self.assertEqual(translate_dot_module_name_to_bazel("abc.def.ghi.ghi"), "//abc/def/ghi")
        # External repos
        self.assertEqual(translate_dot_module_name_to_bazel("@ext.abc"), "@ext//:abc")
        self.assertEqual(translate_dot_module_name_to_bazel("@ext.abc.def"), "@ext//abc:def")
        self.assertEqual(translate_dot_module_name_to_bazel("@ext.abc.def.xyz"), "@ext//abc/def:xyz")

if __name__ == '__main__':
    unittest.main()
