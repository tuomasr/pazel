"""Output a BUILD file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Used for installing pip packages. See https://github.com/bazelbuild/rules_python
REQUIREMENT = """load("@my_deps//:requirements.bzl", "requirement")"""


def _append_newline(source):
    """Add newline to a string if it does not end with a newline."""
    return source if source.endswith('\n') else source + '\n'


def output_build_file(build_source, ignored_rules, output_extension, build_file_path):
    """Output a BUILD file.

    Args:
        build_source (str): The contents of the BUILD file to output.
        ignored_rules (list of str): Rules the user wants to keep as is.
        output_extension (OutputExtension): User-defined header and footer.
        build_file_path (str): Path to the BUILD file in which build_source is written.
    """
    header = ''

    if output_extension.header:
        header += _append_newline(output_extension.header)

    # If the BUILD file contains external packages, add the Bazel method for installing them.
    if 'requirement("' in build_source:
        header += _append_newline(REQUIREMENT)

    # Add ignored load statements right after the header.
    remaining_ignored_rules = []

    if ignored_rules:
        for ignored_rule in ignored_rules:
            if 'load(' in ignored_rule:
                header += _append_newline(ignored_rule)
            else:
                remaining_ignored_rules.append(ignored_rule)

    # If a header exists, add a newline between it and the rules.
    if header:
        header += '\n'

    output = header + build_source

    # Add other ignored rules than load statements to the bottom, separated by newlines.
    if remaining_ignored_rules:
        output = output.rstrip()
        output += '\n' + '\n'.join(remaining_ignored_rules)

    # Add the footer, separated by a newline.
    if output_extension.footer:
        output += 2*'\n' + _append_newline(output_extension.footer)

    with open(build_file_path, 'w') as build_file:
        output = _append_newline(output)
        build_file.write(output)
