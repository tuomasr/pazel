"""Helper functions for generating Bazel BUILD files for a Python project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import importlib
import os
import platform
import re
import sys
import traceback

from pazel.script_type import ScriptType


def contains_py_files(path):
    """Check if the given path contains at least one .py/.pyc file."""
    files = os.listdir(path)
    contains_py = any(f.endswith('.py') or f.endswith('.pyc') for f in files)

    return contains_py


def is_valid_python_file(path):
    """Check whether a file in path is a valid Python file."""
    valid = False

    if os.path.isfile(path) and path.endswith('.py'):
        valid = True

    return valid


def _is_in_stdlib(module, some_object):
    """Check if a given module is part of the Python standard library."""
    # Clear PYTHONPATH temporarily and try importing the given module.
    original_sys_path = sys.path
    lib_path = os.path.dirname(traceback.__file__)
    sys.path = [lib_path]

    # On Mac, some extra library paths are required.
    if 'darwin' in platform.system().lower():
        for path in original_sys_path:
            if 'site-packages' not in path:
                sys.path.append(path)

    in_stdlib = False

    try:
        module = importlib.import_module(module)

        if some_object:
            getattr(module, some_object)

        in_stdlib = True
    except (ImportError, AttributeError):
        pass

    sys.path = original_sys_path

    return in_stdlib


def is_installed(module, some_object=None, pre_installed_packages=False):
    """Check if a given module is installed and whether some_object is found in it."""
    installed = False

    # If the application runs inside e.g. a virtualenv that already contains some requirements,
    # then try importing the module. If it fails, then the module is not yet installed.
    if pre_installed_packages:
        try:
            module = importlib.import_module(module)

            if some_object:
                getattr(module, some_object)

            installed = True
        except (ImportError, AttributeError):
            installed = False
    else:   # If we have a clean install, then check if the module is in the standard library.
        installed = _is_in_stdlib(module, some_object)

    return installed


def parse_enclosed_expression(source, start, token):
    """Parse an expression enclosed by a token and its counterpart."""
    if token == '(':
        closing_token = ')'
    elif token == '[':
        closing_token = ']'
    else:
        raise ValueError("No closing token defined for %s." % token)

    start2 = source.find(token, start)
    assert start2 > start, "Could not locate the opening token."
    open_tokens = 0
    end = None

    for end_idx, char in enumerate(source[start2:], start2):
        if char == token:
            open_tokens += 1
        elif char == closing_token:
            open_tokens -= 1

        if open_tokens == 0:
            end = end_idx + 1
            break

    assert end, "Could not locate the closing token."

    return source[start:end]
