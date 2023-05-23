"""Entrypoint for generating Bazel BUILD files for a Python project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

from pazel.generate_rule import parse_script_and_generate_rule
from pazel.helpers import get_build_file_path
from pazel.helpers import is_ignored
from pazel.helpers import is_python_file
from pazel.helpers import has_extension
from pazel.output_build import output_build_file
from pazel.parse_build import get_ignored_rules
from pazel.pazel_extensions import parse_pazel_extensions


def app(input_path, project_root, contains_pre_installed_packages, pazelrc_path):
    """Generate BUILD file(s) for a Python script or a directory of Python scripts.

    Args:
        input_path (str): Path to a Python file or to a directory containing Python file(s) for
        which BUILD files are generated.
        project_root (str): Imports in the Python files are relative to this path.
        contains_pre_installed_packages (bool): Whether the environment is allowed to contain
            pre-installed packages or whether only the Python standard library is available.
        pazelrc_path (str): Path to .pazelrc config file for customizing pazel.

    Raises:
        RuntimeError: input_path does is not a directory or a Python file.
    """
    # Parse user-defined extensions to pazel.
    output_extension, custom_bazel_rules, custom_bazel_rules_extra_extensions, \
        custom_import_inference_rules, import_name_to_pip_name, \
        local_import_name_to_dep, requirement_load = parse_pazel_extensions(pazelrc_path)

    # Handle directories.
    if os.path.isdir(input_path):
        # Traverse the directory recursively.
        for dirpath, _, filenames in os.walk(input_path):
            build_source = ''

            # Parse ignored rules in an existing BUILD file, if any.
            build_file_path = get_build_file_path(dirpath)
            ignored_rules = get_ignored_rules(build_file_path)

            for filename in sorted(filenames):
                path = os.path.join(dirpath, filename)

                # If a Python file is met and it is not in the list of ignored rules,
                # generate a Bazel rule for it.
                if (is_python_file(path) or has_extension(path, custom_bazel_rules_extra_extensions)) and not is_ignored(path, ignored_rules):
                    new_rule = parse_script_and_generate_rule(path, project_root,
                                                              contains_pre_installed_packages,
                                                              custom_bazel_rules,
                                                              custom_import_inference_rules,
                                                              import_name_to_pip_name,
                                                              local_import_name_to_dep)

                    # Add the new rule and a newline between it and any previous rules.
                    if new_rule:
                        if build_source:
                            build_source += 2*'\n'

                        build_source += new_rule

            # If Python files were found, output the BUILD file.
            if build_source != '' or ignored_rules:
                output_build_file(build_source, ignored_rules, output_extension, custom_bazel_rules,
                                  build_file_path, requirement_load)
    # Handle single Python file.
    elif is_python_file(input_path):
        build_source = ''

        # Parse ignored rules in an existing BUILD file, if any.
        build_file_path = get_build_file_path(input_path)
        ignored_rules = get_ignored_rules(build_file_path)

        # Check that the script is not in the list of ignored rules.
        if not is_ignored(input_path, ignored_rules):
            build_source = parse_script_and_generate_rule(input_path, project_root,
                                                          contains_pre_installed_packages,
                                                          custom_bazel_rules,
                                                          custom_import_inference_rules,
                                                          import_name_to_pip_name,
                                                          local_import_name_to_dep)

        # If Python files were found, output the BUILD file.
        if build_source != '' or ignored_rules:
            output_build_file(build_source, ignored_rules, output_extension, custom_bazel_rules,
                              build_file_path, requirement_load)
    else:
        raise RuntimeError("Invalid input path %s." % input_path)


def main():
    """Parse command-line flags and generate the BUILD files accordingly."""
    parser = argparse.ArgumentParser(description='Generate Bazel BUILD files for a Python project.')

    working_directory = os.getcwd()
    default_pazelrc_path = os.path.join(working_directory, '.pazelrc')

    parser.add_argument('input_path', nargs='?', type=str, default=working_directory,
                        help='Target Python file or directory of Python files.'
                        ' Defaults to the current working directory.')
    parser.add_argument('-r', '--project-root', type=str, default=working_directory,
                        help='Project root directory. Imports are relative to this path.'
                        ' Defaults to the current working directory.')
    parser.add_argument('-p', '--pre-installed-packages', action='store_true',
                        help='Target will be run in an environment with packages pre-installed.'
                        ' Affects which packages are listed as pip-installable.')
    parser.add_argument('-c', '--pazelrc', type=str, default=default_pazelrc_path,
                        help='Path to .pazelrc file.')

    args = parser.parse_args()

    # If the user specified custom .pazelrc file, then check that it exists.
    custom_pazelrc_path = args.pazelrc != default_pazelrc_path

    if custom_pazelrc_path:
        assert os.path.isfile(args.pazelrc), ".pazelrc file %s not found." % args.pazelrc

    app(args.input_path, args.project_root, args.pre_installed_packages, args.pazelrc)
    print('Generated BUILD files for %s.' % args.input_path)


if __name__ == "__main__":
    main()
