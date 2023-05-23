"""Classes for identifying Bazel rule type of a script and generating new rules to BUILD files."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

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


class BazelRule(object):
    """Base class defining the interface for parsing Bazel rules.

    pazel-native rule classes as well as custom rule classes need to implement this interface.
    """

    # Required class variables.
    is_test_rule = None
    template = None
    rule_identifier = None

    @staticmethod
    def applies_to(script_name, script_source, script_extension):
        """Check whether this rule applies to a given script.

        Args:
            script_name (str): Name of a Python script without the .py suffix.
            script_source (str): Source code of the script.

        Returns:
            applies (bool): Whether this Bazel rule can be used to represent the script.
        """
        raise NotImplementedError()

    @staticmethod
    def find_existing(build_source, script_filename):
        """Find existing rule for a given script.

        Args:
            build_source (str): Source code of an existing BUILD file.
            script_filename (str): Name of a Python script.

        Returns:
            match (MatchObject or None): Match found in the BUILD file or None if no matches.
        """
        # 'srcs' should contain the script filename.
        pattern = 'srcs\s*=\s*\["' + script_filename + '"\]'
        match = re.search(pattern, build_source)

        return match

    @staticmethod
    def get_load_statement():
        """If the rule requires a special 'load' statement, return it, otherwise return None."""
        return None


class PyBinaryRule(BazelRule):
    """Class for representing Bazel-native py_binary."""

    # Required class variables.
    is_test_rule = False    # Is this a test rule?
    template = PY_BINARY_TEMPLATE   # Filled version of this will be written to the BUILD file.
    rule_identifier = 'py_binary'   # The name of the rule.

    @staticmethod
    def applies_to(script_name, script_source, script_extension):
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
        is_test = PyTestRule.applies_to(script_name, script_source, script_extension)

        applies = len(entrypoints) > 0 and not is_test

        return applies


class PyLibraryRule(BazelRule):
    """Class for representing Bazel-native py_library."""

    # Required class variables.
    is_test_rule = False    # Is this a test rule?
    template = PY_LIBRARY_TEMPLATE  # Filled version of this will be written to the BUILD file.
    rule_identifier = 'py_library'  # The name of the rule.

    @staticmethod
    def applies_to(script_name, script_source, script_extension):
        """Check whether this rule applies to a given script.

        Args:
            script_name (str): Name of a Python script without the .py suffix.
            script_source (str): Source code of the script.

        Returns:
            applies (bool): Whether this Bazel rule can be used to represent the script.
        """
        is_test = PyTestRule.applies_to(script_name, script_source, script_extension)
        is_binary = PyBinaryRule.applies_to(script_name, script_source, script_extension)

        applies = not (is_test or is_binary)

        return applies


class PyTestRule(BazelRule):
    """Class for representing Bazel-native py_test."""

    # Required class variables.
    is_test_rule = True     # Is this a test rule?
    template = PY_TEST_TEMPLATE     # Filled version of this will be written to the BUILD file.
    rule_identifier = 'py_test'     # The name of the rule.

    @staticmethod
    def applies_to(script_name, script_source, script_extension):
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


def get_native_bazel_rules():
    """Return a copy of the pazel-native classes implementing BazelRule."""
    return [PyBinaryRule, PyLibraryRule, PyTestRule]    # No custom classes here.


def infer_bazel_rule_type(script_path, script_source, custom_rules):
    """Infer the Bazel rule type given the path to the script and its source code.

    Args:
        script_path (str): Path to a Python script.
        script_source (str): Source code of the Python script.
        custom_rules (list of BazelRule classes): User-defined classes implementing BazelRule.

    Returns:
        bazel_rule_type (BazelRule): Rule object representing the type of the Python script.

    Raises:
        RuntimeError: If zero or more than one Bazel rule is found for the current script.
    """
    script_basename = os.path.basename(script_path)
    script_extension_index = script_basename.rfind('.')
    script_name = script_basename[:script_extension_index]
    script_extension = script_basename[script_extension_index:]

    bazel_rule_types = []

    native_rules = get_native_bazel_rules()
    registered_rules = native_rules + custom_rules

    for bazel_rule in registered_rules:
        if bazel_rule.applies_to(script_name, script_source, script_extension):
            bazel_rule_types.append(bazel_rule)

    if not bazel_rule_types:
        raise RuntimeError("No suitable Bazel rule type found for %s." % script_path)
    elif len(bazel_rule_types) > 1:
        # If the script is recognized by pazel native rule(s) and one exactly custom rule, then use
        # the custom rule. This is because the pazel native rules may generate false positives.
        is_custom = [rule not in native_rules for rule in bazel_rule_types]
        one_custom = sum(is_custom) == 1

        if one_custom:
            custom_bazel_rule_idx = is_custom.index(True)
            return bazel_rule_types[custom_bazel_rule_idx]
        else:
            raise RuntimeError("Multiple Bazel rule types (%s) found for %s."
                               % (bazel_rule_types, script_path))

    return bazel_rule_types[0]
