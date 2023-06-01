"""Helper functions for generating Bazel BUILD files for a Python project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast
import importlib
import os
import platform
import sys
import traceback


def contains_python_file(directory):
    """Check if the given directory contains at least one .py/.pyc file.

    Args:
        directory (str):

    Returns:
        contains_py (bool): Whether the directory contains at least one Python file.
    """
    files = os.listdir(directory)
    contains_py = any(f.endswith('.py') or f.endswith('.pyc') for f in files)

    return contains_py


def get_build_file_path(path):
    """Get path to a BUILD file next to a given path.

    Args:
        path (str): Path to a file or directory.

    Returns
        build_file_path (str): Path to the BUILD in the given directory or in the directory
            containing the given file.
    """
    if os.path.isdir(path):
        directory = path
    else:
        directory = os.path.dirpath(path)

    build_file_path = os.path.join(directory, 'BUILD')

    return build_file_path


def is_ignored(script_path, ignored_rules):
    """Check whether the given script is in ignored rules.

    Args:
        script_path (str): Path to a Python script.
        ignored_rules (list of str): Ignored Bazel rules.

    Returns:
        ignored (bool): Whether the script should be ignored.
    """
    ignored = False

    script_file_name = os.path.basename(script_path)

    for ignored_rule in ignored_rules:
        # Parse the rule to an AST node.
        try:
            node = ast.parse(ignored_rule)
        except SyntaxError:
            raise SyntaxError("Invalid syntax in an ignored rule %s." % ignored_rule)

        assert len(node.body) == 1, "Unsupported rule type %s." % ignored_rule

        # Check keyword arguments in the rule. If the 'srcs' argument contains the script file name,
        # then the script should be ignored.
        func_call = node.body[0].value

        for keyword in func_call.keywords:
            if keyword.arg == 'srcs':
                elements = keyword.value.elts

                assert len(elements) == 1, \
                    "Multiple source files not supported in %s." % ignored_rule

                if elements[0].s == script_file_name:
                    ignored = True
                    break

        # The script file name may also given as a positional argument.
        for positional in func_call.args:
            if positional.s == script_file_name:
                ignored = True
                break

    return ignored

def has_extension(path, extensions):
    """Check whether the file is a file of the given types.

    Args:
        path (str): Path to a file.
        extensions (list[str]): File extensions to return true for. 

    Returns:
        valid (bool): The file in path is a Python file.
    """
    valid = False

    for extension in extensions:
        if os.path.isfile(path) and path.endswith(extension):
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


def is_installed(module, some_object=None, contains_pre_installed_packages=False):
    """Check if a given module is installed and whether some_object is found in it.

    Args:
        module (str): Name of a module.
        some_object (str): Name of some object in the module. Can be None.
        contains_pre_installed_packages (bool): Whether the environment contains external packages.

    Returns:
        installed (bool): The module is installed in the current environment.
    """
    installed = False

    # If the application runs inside e.g. a virtualenv that already contains some requirements,
    # then try importing the module. If it fails, then the module is not yet installed.
    if contains_pre_installed_packages:
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


def parse_enclosed_expression(source, start, opening_token):
    """Parse an expression enclosed by a token and its counterpart.

    Args:
        source (str): Source code of a Bazel BUILD file, for example.
        start (int): Index at which an expression starts.
        opening_token (str): A character '(' or '[' that opens an expression.

    Returns:
        expression (str): The whole expression that contains the opening and closing tokens.

    Raises:
        NotImplementedError: If parsing is not implemented for the given opening token.
    """
    if opening_token == '(':
        closing_token = ')'
    elif opening_token == '[':
        closing_token = ']'
    else:
        raise NotImplementedError("No closing token defined for %s." % opening_token)

    start2 = source.find(opening_token, start)
    assert start2 > start, "Could not locate the opening token %s." % opening_token
    open_tokens = 0
    end = None

    for end_idx, char in enumerate(source[start2:], start2):
        if char == opening_token:
            open_tokens += 1
        elif char == closing_token:
            open_tokens -= 1

        if open_tokens == 0:
            end = end_idx + 1
            break

    assert end, "Could not locate the closing token %s." % closing_token

    expression = source[start:end]

    return expression
