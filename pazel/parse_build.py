"""Parse existing BUILD files to infer data dependencies and test sizes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re

from pazel.helpers import parse_enclosed_expression
from pazel.script_type import ScriptType


def find_existing_rule(build_file_path, script_filename, script_type):
    """Find Bazel rule for a given script in a BUILD file."""
    # Read the existing BUILD file if there is one.
    try:
        with open(build_file_path, 'r') as f:
            build_source = f.read()
    except IOError:
        return None

    rule_start = 'py_library('

    if script_type == ScriptType.BINARY:
        rule_start = 'py_binary('
    elif script_type == ScriptType.TEST:
        rule_start = 'py_test('

    # Find the start of the Bazel Python rule corresponding to the current script.
    pattern = 'srcs\s*=\s*\["' + script_filename + '"\]'
    m = re.search(pattern, build_source)

    if m is None:
        return None

    start = build_source.rfind(rule_start, 0, m.start())

    assert start, "Could not locate the start of the Bazel Python rule for %s." % script_filename

    # Find the rule by matching opening and closing parentheses.
    rule = parse_enclosed_expression(build_source, start, '(')

    return rule


def find_existing_test_size(script_path):
    """Check if the existing Bazel Python rule in a BUILD file contains test size."""
    script_dir = os.path.dirname(script_path)
    script_filename = os.path.basename(script_path)
    build_file_path = os.path.join(script_dir, 'BUILD')

    rule = find_existing_rule(build_file_path, script_filename, ScriptType.TEST)

    # Test size is not set.
    if rule is None:
        return None

    # Search for the test size.
    m = re.findall('size\s*=\s*\"(small|medium|large|enormous)\"', rule)

    num_matches = len(m)

    if num_matches > 0:
        assert num_matches == 1, "Found multiple test size matches in %s." % rule
        return m[0]

    return None


def find_existing_data_deps(script_path, script_type):
    """Check if the existing Bazel Python rule in a BUILD file contains data dependencies."""
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
    m = re.search('data\s*=\s*\[', rule)

    if m:
        data = parse_enclosed_expression(rule, m.start(), '[')

    # Data deps defined by a call to 'glob'.
    m = re.search('data\s*=\s*glob\(', rule)

    if m:
        data = parse_enclosed_expression(rule, m.start(), '(')

    return data


def infer_python_rule_type(script_path, source):
    """Infer the type of the rule given the path to the script and its source code."""
    # Check if there is indentation level 0 code that launches a function.
    entrypoints = re.findall('\nif __name__ == "__main__":', source)
    entrypoints += re.findall('\n\S+\([\S+]?\)', source)
    binary = len(entrypoints) > 0

    # Check the file name for 'test' and check if the source code contains any tests functions.
    script_name = os.path.basename(script_path).replace('.py', '')
    tests = re.findall('def test_', source)
    test = (script_name.startswith('test_') or script_name.endswith('_test')) and len(tests) > 0

    script_type = ScriptType.LIBRARY

    if binary:
        script_type = ScriptType.BINARY
    if test:
        script_type = ScriptType.TEST

    return script_type
    