"""Entrypoint for generating Bazel BUILD files for a Python project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

from pazel.generate_rule import parse_script_and_generate_rule
from pazel.helpers import is_python_file
from pazel.output_build import output_build_file


def app(input_path, project_root, contains_pre_installed_packages):
    """Generate BUILD file(s) for a Python script or a directory of Python scripts.

    Args:
        input_path (str): Path to a Python file or to a directory containing Python file(s) for
        which BUILD files are generated.
        project_root (str): Imports in the Python files are relative to this path.
        contains_pre_installed_packages (bool): Whether the environment is allowed to contain
        pre-installed packages or whether only the Python standard library is available.

    Raises:
        RuntimeError: input_path does is not a directory or a Python file.
    """
    # Handle directories.
    if os.path.isdir(input_path):
        # Traverse the directory recursively.
        for dirpath, _, filenames in os.walk(input_path):
            build_source = ''

            for filename in sorted(filenames):
                path = os.path.join(dirpath, filename)

                # If a Python file is met, generate a Bazel rule for it.
                if is_python_file(path):
                    build_source += parse_script_and_generate_rule(path, project_root,
                                                                   contains_pre_installed_packages)
                    build_source += 2*'\n'  # Add newline between rules.

            # If Python files were found, output the BUILD file.
            if build_source != '':
                output_build_file(build_source, dirpath)
    # Handle single Python file.
    elif is_python_file(input_path):
        build_source = parse_script_and_generate_rule(input_path, project_root,
                                                      contains_pre_installed_packages)

        output_build_file(build_source, os.path.dirpath(input_path))
    else:
        raise RuntimeError("Invalid input path %s." % input_path)


def main():
    """Parse command-line flags and generate the BUILD files accordingly."""
    parser = argparse.ArgumentParser(description='Generate Bazel BUILD files for a Python project.')

    working_directory = os.getcwd()

    parser.add_argument('input_path', nargs='?', type=str, default=working_directory,
                        help='Target Python file or directory of Python files.'
                        ' Defaults to the current working directory.')
    parser.add_argument('-r', '--project-root', type=str, default=working_directory,
                        help='Project root directory. Imports are relative to this path.'
                        ' Defaults to the current working directory.')
    parser.add_argument('-p', '--pre-installed-packages', action='store_true',
                        help='Target will be run in an environment with packages pre-installed.'
                        ' Affects which packages are listed as pip-installable.')

    args = parser.parse_args()

    app(args.input_path, args.project_root, args.pre_installed_packages)
    print('Generated BUILD files for %s.' % args.input_path)


if __name__ == "__main__":
    main()
