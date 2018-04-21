"""Output a BUILD file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Used for installing pip packages. See https://github.com/bazelbuild/rules_python
REQUIREMENT = """load("@my_deps//:requirements.bzl", "requirement")"""


def _append_newline(source):
    """Add newline to a string if it does not end with a newline."""
    return source if source.endswith('\n') else source + '\n'


def output_build_file(build_source, ignored_rules, extensions, build_file_path):
    """Output a BUILD file.

    Args:
        build_source (str): The contents of the BUILD file to output.
        ignored_rules (list of str): Rules the user wants to keep as is.
        extensions (PazelExtension): User-defined extensions to pazel.
        build_file_path (str): Path to the BUILD file in which build_source is written.
    """
    header = _append_newline(extensions.header)

    # If the BUILD file contains external packages, add the Bazel method for installing them.
    if 'requirement("' in build_source:
        header += _append_newline(REQUIREMENT)

    build_source = header + '\n' + build_source

    # Add ignored rules to the bottom, separated by newlines.
    if ignored_rules:
        build_source = build_source.rstrip()
        build_source += '\n' + '\n'.join(ignored_rules) + 2*'\n'

    build_source += _append_newline(extensions.footer)

    with open(build_file_path, 'w') as build_file:
        build_file.write(build_source)
