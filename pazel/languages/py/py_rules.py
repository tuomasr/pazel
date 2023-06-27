"""Classes for identifying Bazel rule type of a Python script and generating new rules to BUILD files."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

from pazel.bazel_rules import BazelRule


# These templates will be filled and used to generate BUILD files.
# Note that both 'data' and 'deps' can be empty in which case they are left out from the rules.
PY_BINARY_TEMPLATE = """py_binary(
    name = "{name}",
    srcs = ["{name}.py"],
    {data}
    {deps}
)"""

PY_LIBRARY_TEMPLATE = """py_library(
    name = "{name}",
    srcs = ["{name}.py"],
    {data}
    {deps}
)"""

PY_TEST_TEMPLATE = """py_test(
    name = "{name}",
    srcs = ["{name}.py"],
    size = "{size}",
    {data}
    {deps}
)"""

class PyBinaryRule(BazelRule):
    """Class for representing Bazel-native py_binary."""

    # Required class variables.
    is_test_rule = False    # Is this a test rule?
    template = PY_BINARY_TEMPLATE   # Filled version of this will be written to the BUILD file.
    rule_identifier = 'py_binary'   # The name of the rule.

    @staticmethod
    def applies_to(script_name, script_source):
        """Check whether this rule applies to a given script.

        Args:
            script_name (str): Name of a Python script without the .py suffix.
            script_source (str): Source code of the script.

        Returns:
            applies (bool): Whether this Bazel rule can be used to represent the script.
        """
        # Check if there is indentation level 0 code that launches a function.
        entrypoints = re.findall('\nif\s*__name__\s*==\s*["\']__main__["\']\s*:', script_source)
        entrypoints += re.findall('\n\S+\([\S+]?\)', script_source)

        # Rule out tests using unittest.
        is_test = PyTestRule.applies_to(script_name, script_source)

        applies = len(entrypoints) > 0 and not is_test

        return applies


class PyLibraryRule(BazelRule):
    """Class for representing Bazel-native py_library."""

    # Required class variables.
    is_test_rule = False    # Is this a test rule?
    template = PY_LIBRARY_TEMPLATE  # Filled version of this will be written to the BUILD file.
    rule_identifier = 'py_library'  # The name of the rule.

    @staticmethod
    def applies_to(script_name, script_source):
        """Check whether this rule applies to a given script.

        Args:
            script_name (str): Name of a Python script without the .py suffix.
            script_source (str): Source code of the script.

        Returns:
            applies (bool): Whether this Bazel rule can be used to represent the script.
        """
        is_test = PyTestRule.applies_to(script_name, script_source)
        is_binary = PyBinaryRule.applies_to(script_name, script_source)

        applies = not (is_test or is_binary)

        return applies


class PyTestRule(BazelRule):
    """Class for representing Bazel-native py_test."""

    # Required class variables.
    is_test_rule = True     # Is this a test rule?
    template = PY_TEST_TEMPLATE     # Filled version of this will be written to the BUILD file.
    rule_identifier = 'py_test'     # The name of the rule.

    @staticmethod
    def applies_to(script_name, script_source):
        """Check whether this rule applies to a given script.

        Args:
            script_name (str): Name of a Python script without the .py suffix.
            script_source (str): Source code of the script.

        Returns:
            applies (bool): Whether this Bazel rule can be used to represent the script.
        """
        imports_unittest = len(re.findall('import unittest', script_source)) > 0 or \
            len(re.findall('from unittest', script_source)) > 0
        uses_unittest = len(re.findall('unittest.TestCase', script_source)) > 0 or \
            len(re.findall('TestCase', script_source)) > 0
        test_filename = script_name.startswith('test_') or script_name.endswith('_test')

        applies = test_filename and imports_unittest and uses_unittest

        return applies


def get_bazel_rules():
    """Return a copy of the pazel-native classes implementing BazelRule."""
    return [PyBinaryRule, PyLibraryRule, PyTestRule]    # No custom classes here.
