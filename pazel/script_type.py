"""Enum class to represent Python script type."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re


class ScriptType(object):
    """Custom enum-like type for Python script type."""

    BINARY = 0
    LIBRARY = 1
    TEST = 2


def infer_python_rule_type(script_path, script_source):
    """Infer the type of the rule given the path to the script and its source code.

    Args:
        script_path (str): Path to a Python script.
        script_source (str): Source code of the Python script.

    Returns:
        script_type (ScripType): Enum object representing the type of the script.
    """
    # Check if there is indentation level 0 code that launches a function.
    entrypoints = re.findall('\nif __name__ == "__main__":', script_source)
    entrypoints += re.findall('\n\S+\([\S+]?\)', script_source)
    binary = len(entrypoints) > 0

    # The script can still be a test if there is indentation level 0 code. Thus, update script type
    # if the file name contains 'test' or if the source code contains any tests functions.
    script_name = os.path.basename(script_path).replace('.py', '')  # Strip the file suffix.
    tests = re.findall('def test_', script_source)
    test = (script_name.startswith('test_') or script_name.endswith('_test')) and len(tests) > 0

    script_type = ScriptType.LIBRARY

    if binary:
        script_type = ScriptType.BINARY
    if test:
        script_type = ScriptType.TEST

    return script_type
