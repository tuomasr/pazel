
import unittest

from pazel.generate_rule import infer_bazel_rule_types
from pazel.languages.proto.proto_rules import ProtoLibraryRule
from pazel.languages.proto.proto_rules import PyProtoLibraryRule

proto_file_src = """
syntax = "proto3";

package com.testing;

message MyProto {
  string text = 1;
}
"""

class TestProtoLibraryRule(unittest.TestCase):
    """Test ProtoLibraryRule."""

    def test_applies_to(self):
        """Test ProtoLibraryRule.applies_to for different script sources."""
        self.assertEqual(ProtoLibraryRule.applies_to("my.proto", proto_file_src), True)
        self.assertEqual(PyProtoLibraryRule.applies_to("my.proto", proto_file_src), True)

class TestBazelRuleInference(unittest.TestCase):
    """Test inferring the Bazel rule type of a script."""

    def test_infer_bazel_rule_types(self):
        """Test inferring the Bazel rule type."""
        custom_rules = []

        self.assertEqual(
            infer_bazel_rule_types("my.proto", proto_file_src, custom_rules),
            [ProtoLibraryRule, PyProtoLibraryRule])

if __name__ == '__main__':
    unittest.main()
