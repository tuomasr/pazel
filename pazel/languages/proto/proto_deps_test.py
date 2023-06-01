"""Test parsing imports from a Python file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

from pazel.languages.proto.proto_deps import get_imports


class TestParseImports(unittest.TestCase):
    """Test helper functions."""

    def test_get_imports(self):
        """Test parse_enclosed_expression."""
        script_source = """
import "google/protobuf/duration.proto";
import "foo/public/proto/bar.proto";

message MyMessage {
    google.protobuf.Duration duration = 1;
    foo.Bar bar = 2;
}
"""

        packages, from_imports = get_imports(script_source)

        expected_packages = []
        expected_from_imports = [
            ('google.protobuf', 'duration_proto'),
            ('foo.public.proto', 'bar_proto')]

        self.assertEqual(packages, expected_packages)
        self.assertEqual(from_imports, expected_from_imports)


if __name__ == '__main__':
    unittest.main()
