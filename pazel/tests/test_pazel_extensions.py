"""Test parsing user-defined extensions to pazel."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

from pazel.pazel_extensions import parse_pazel_extensions


class TestParseImports(unittest.TestCase):
    """Test parsing user-defined extensions to pazel."""

    def test_invalid_pazelrc_file(self):
        """Test that parse_pazel_extensions returns defaults for an invalid pazelrc file."""
        pazelrc_path = 'fail'

        output_extension, custom_bazel_rules, custom_bazel_rules_extra_extensions, \
            custom_import_inference_rules, import_name_to_pip_name, \
            local_import_name_to_dep, requirement_load \
            = parse_pazel_extensions(pazelrc_path)

        self.assertEqual(output_extension.header, '')
        self.assertEqual(output_extension.footer, '')
        self.assertEqual(custom_bazel_rules, [])
        self.assertEqual(custom_bazel_rules_extra_extensions, [])
        self.assertEqual(custom_import_inference_rules, [])
        self.assertEqual(import_name_to_pip_name, dict())
        self.assertEqual(local_import_name_to_dep, dict())
        self.assertEqual(requirement_load, 'load("@my_deps//:requirements.bzl", "requirement")')


if __name__ == '__main__':
    unittest.main()
