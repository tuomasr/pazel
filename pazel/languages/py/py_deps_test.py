"""Test parsing imports from a Python file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

from pazel.languages.py.py_deps import get_imports


class TestParseImports(unittest.TestCase):
    """Test helper functions."""

    def test_get_imports(self):
        """Test parse_enclosed_expression."""
        script_source = """
import ast
from ast import parse
from foo import bar as abc
from asd import \
    wasd
"""

        packages, from_imports = get_imports(script_source)

        expected_packages = [('ast', None)]
        expected_from_imports = [('ast', 'parse'), ('foo', 'bar'), ('asd', 'wasd')]

        self.assertEqual(packages, expected_packages)
        self.assertEqual(from_imports, expected_from_imports)


if __name__ == '__main__':
    unittest.main()
