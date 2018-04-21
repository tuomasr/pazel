"""Test helper functions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

from pazel.helpers import parse_enclosed_expression


class TestHelpers(unittest.TestCase):
    """Test helper functions."""

    def test_parse_enclosed_expression(self):
        """Test parse_enclosed_expression."""
        expected_expression = """py_library(
            name = "foo",
            srcs = ["foo.py"],
            deps = [
                "//bar",
                requirement("pyyaml"),
            ],
        )"""

        source = """some text
        more text

        {expression}

        more text
        end
        """.format(expression=expected_expression)

        start = source.find('py_library')   # Find the index at which the expression starts.

        expression = parse_enclosed_expression(source, start, '(')

        self.assertEqual(expression, expected_expression)


if __name__ == '__main__':
    unittest.main()
