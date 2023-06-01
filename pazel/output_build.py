"""Output a BUILD file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re


def _append_newline(source):
    """Add newline to a string if it does not end with a newline."""
    return source if source.endswith('\n') else source + '\n'


def output_build_file(build_source, ignored_rules, output_extension, bazel_rule_types,
                      build_file_path, requirement_load):
    """Output a BUILD file.

    Args:
        build_source (str): The contents of the BUILD file to output.
        ignored_rules (list of str): Rules the user wants to keep as is.
        output_extension (OutputExtension): User-defined header and footer.
        bazel_rule_types (list of BazelRule classes): BazelRule classes that were used to render the build_source.
        build_file_path (str): Path to the BUILD file in which build_source is written.
        requirement_load (str): Statement for loading the 'requirement' rule.
    """
    header = ''

    if output_extension.header:
        header += _append_newline(output_extension.header)

    # Categorize ignored rules to 'load' statements and other remaining rules.
    ignored_load_statements = []
    remaining_ignored_rules = []

    if ignored_rules:
        for ignored_rule in ignored_rules:
            if 'load(' in ignored_rule:
                ignored_load_statements.append(ignored_rule)
            else:
                remaining_ignored_rules.append(ignored_rule)

    # If the BUILD file contains external packages, add the 'load' statement for installing them.
    # Check that this statement is not in the ignored 'load' statements.
    ignored_source = '\n'.join(remaining_ignored_rules)

    if any(['requirement("' in source for source in (build_source, ignored_source)]):
        in_ignored_load_statements = any(['requirement("' in statement for statement in
                                          ignored_load_statements])

        if not in_ignored_load_statements:
            header += _append_newline(requirement_load)

    # If the BUILD source contains custom Bazel rules, then add the load statements for them unless
    # the load statements are already in the ignored load statements.
    load_statements = []
    for bazel_rule_type in bazel_rule_types:
        rule_identifier = bazel_rule_type.rule_identifier
        in_ignored_load_statements = any([rule_identifier in statement for statement in
                                          ignored_load_statements])

        if rule_identifier and not in_ignored_load_statements:
            load_statement = bazel_rule_type.get_load_statement()
            if load_statement:
                load_statements.append(load_statement)

    for load_statement in sorted(load_statements):
        header += _append_newline(load_statement)

    # Add ignored load statements right after the header.
    for ignored_load in ignored_load_statements:
        header += _append_newline(ignored_load)

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

        # Remove possible duplicate newlines (the user may have added such accidentally).
        output = re.sub('\n\n\n*', '\n\n', output)

        build_file.write(output)
