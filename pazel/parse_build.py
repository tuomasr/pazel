"""Parse existing BUILD files."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

from pazel.helpers import parse_enclosed_expression


def find_existing_rule(build_file_path, script_filename, bazel_rule_type):
    """Find Bazel rule for a given Python script in a BUILD file.

    Args:
        build_file_path (str): Path to an existing BUILD file that may contain a rule for a given
            Python script.
        script_filename (str): File name of the Python script.
        bazel_rule_type (Rule class): pazel-native or a custom class implementing BazelRule.

    Returns:
        rule (str): Existing Bazel rule for the Python script. If there is no rule, then None.
    """
    # Read the existing BUILD file if there is one.
    try:
        with open(build_file_path, 'r') as build_file:
            build_source = build_file.read()
    except IOError:
        return None

    # Find existing rules for the current script.
    match = bazel_rule_type.find_existing(build_source, script_filename)

    if match is None:
        return None

    # Find the start of the rule.
    rule_identifier = bazel_rule_type.rule_identifier
    start = match.start()

    # If the match is not the beginning of the rule, then go backwards to the start of the rule.
    if build_source[start:start + len(rule_identifier)] != rule_identifier:
        start = build_source.rfind(bazel_rule_type.rule_identifier, 0, start)

    rule = None
    if start != -1:
        # Find the rule by matching opening and closing parentheses.
        rule = parse_enclosed_expression(build_source, start, '(')

    return rule


def find_existing_test_size(script_path, bazel_rule_type):
    """Check if the existing Bazel rule for a Python test contains test size.

    Args:
        script_path (str): Path to a Python file that is a test.
        bazel_rule_type (Rule class): pazel-native or a custom class implementing BazelRule.

    Returns:
        test_size (str): Size of the test (small, medium, etc.) if found in the existing BUILD file.
        If not found, then None is returned.
    """
    if not bazel_rule_type.is_test_rule:
        return None

    script_dir = os.path.dirname(script_path)
    script_filename = os.path.basename(script_path)
    build_file_path = os.path.join(script_dir, 'BUILD')

    rule = find_existing_rule(build_file_path, script_filename, bazel_rule_type)

    # No existing Bazel rules for the given Python file.
    if rule is None:
        return None

    # Search for the test size.
    matches = re.findall('size\s*=\s*\"(small|medium|large|enormous)\"', rule)

    num_matches = len(matches)

    if num_matches > 0:
        assert num_matches == 1, "Found multiple test size matches in %s." % rule
        return matches[0]

    return None


def find_existing_data_deps(script_path, bazel_rule_type):
    """Check if the existing Bazel Python rule in a BUILD file contains data dependencies.

    Args:
        script_path (str): Path to a Python script.
        bazel_rule_type (Rule class): pazel-native or a custom class implementing BazelRule.

    Returns:
        data (str): Data dependencies in the existing rule for the Python script.
    """
    script_dir = os.path.dirname(script_path)
    script_filename = os.path.basename(script_path)
    build_file_path = os.path.join(script_dir, 'BUILD')

    rule = find_existing_rule(build_file_path, script_filename, bazel_rule_type)

    # No matches, no data deps.
    if rule is None:
        return None

    # Search for data deps.
    data = None

    # Data deps are a list.
    match = re.search('data\s*=\s*\[', rule)

    if match:
        data = parse_enclosed_expression(rule, match.start(), '[')

    # Data deps defined by a call to 'glob'.
    match = re.search('data\s*=\s*glob\(', rule)

    if match:
        data = parse_enclosed_expression(rule, match.start(), '(')

    return data


def get_ignored_rules(build_file_path):
    """Check if an existing BUILD file contains rule that should be ignored.

    Args:
        build_file_path (str): Path to an existing BUILD file.

    Returns:
        ignored_rules (list of str): Ignored Bazel rule(s). Empty list if no ignored rules were
            found or if the Bazel BUILD does not exist.
    """
    try:
        with open(build_file_path, 'r') as build_file:
            build_source = build_file.read()
    except IOError:
        return []

    ignored_rules = []

    # pazel ignores rules following the tag "# pazel-ignore". Spaces are ignored within the tag but
    # the line must start with #.
    for match in re.finditer('(?:^|\n)#\s+pazel-ignore\s+', build_source):
        start = match.start()

        rule = parse_enclosed_expression(build_source, start, '(')
        ignored_rules.append(rule)

    return ignored_rules
