import unittest

from pazel.bazel_rules import BazelRule

class TestBazelRule(unittest.TestCase):
    """Test BazelRule base class."""

    def test_applies_to(self):
        """Test BazelRule.applies_to."""
        with self.assertRaises(NotImplementedError):
            BazelRule.applies_to('script_name', 'script_source')

    def test_find_existing(self):
        """Test finding an existing Bazel rule in a BUILD source."""
        build_source = """
py_test(
    name = "test_bazel_rules",
    srcs = ["test_bazel_rules.py"],
    size = "small",
    deps = ["//pazel:bazel_rules"],
)"""
        self.assertIsNotNone(BazelRule.find_existing(build_source, 'test_bazel_rules.py'))
        self.assertIsNone(BazelRule.find_existing(build_source, 'missing.py'))

    def test_get_load_statement(self):
        """Test BazelRule.get_load_statement."""
        self.assertIsNone(BazelRule.get_load_statement())

if __name__ == '__main__':
    unittest.main()
