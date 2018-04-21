"""Parse existing BUILD files to infer data dependencies and test sizes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

from pazel.helpers import parse_enclosed_expression
from pazel.script_type import ScriptType


def find_existing_rule(build_file_path, script_filename, script_type):
    """Find Bazel rule for a given Python script in a BUILD file.

    Args:
        build_file_path (str): Path to an existing BUILD file that may contain a rule for a given
        Python script.
        script_filename (str): File name of the Python script.
        script_type (ScriptType): Enum representing the type of the Python script.

    Returns:
        rule (str): Existing Bazel rule for the Python script. If there is no rule, then None.
    """
    # Read the existing BUILD file if there is one.
    try:
        with open(build_file_path, 'r') as build_file:
            build_source = build_file.read()
    except IOError:
        return None

    rule_start = 'py_library('

    if script_type == ScriptType.BINARY:
        rule_start = 'py_binary('
    elif script_type == ScriptType.TEST:
        rule_start = 'py_test('

    # Find the start of the Bazel Python rule corresponding to the current script.
    pattern = 'srcs\s*=\s*\["' + script_filename + '"\]'
    match = re.search(pattern, build_source)

    if match is None:
        return None

    start = build_source.rfind(rule_start, 0, match.start())

    assert start, "Could not locate the start of the Bazel Python rule for %s." % script_filename

    # Find the rule by matching opening and closing parentheses.
    rule = parse_enclosed_expression(build_source, start, '(')

    return rule


def find_existing_test_size(script_path):
    """Check if the existing Bazel rule for a Python test contains test size.

    Args:
        script_path (str): Path to a Python file that is a test.

    Returns:
        test_size (str): Size of the test (small, medium, etc.) if found in the existing BUILD file.
        If not found, then None is returned.
    """
    script_dir = os.path.dirname(script_path)
    script_filename = os.path.basename(script_path)
    build_file_path = os.path.join(script_dir, 'BUILD')

    rule = find_existing_rule(build_file_path, script_filename, ScriptType.TEST)

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


def find_existing_data_deps(script_path, script_type):
    """Check if the existing Bazel Python rule in a BUILD file contains data dependencies.

    Args:
        script_path (str): Path to a Python script.
        script_type (ScriptType): Enum representing the type of the Python script.

    Returns:
        data (str): Data dependencies in the existing rule for the Python script.
    """
    script_dir = os.path.dirname(script_path)
    script_filename = os.path.basename(script_path)
    build_file_path = os.path.join(script_dir, 'BUILD')

    rule = find_existing_rule(build_file_path, script_filename, script_type)

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
