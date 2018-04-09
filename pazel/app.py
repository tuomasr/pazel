"""Entrypoint for generating Bazel BUILD files for a Python project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

from pazel.gen_rule import parse_script_and_generate_rule
from pazel.helpers import is_valid_python_file


# Used for installing pip packages.
# See https://github.com/bazelbuild/rules_python
REQUIREMENT = """
load("@my_deps//:requirements.bzl", "requirement")"""


HEADER = """package(default_visibility = ["//visibility:public"]){requirement}

"""


def output_build_file(build_source, directory):
    """Output a BUILD file."""
    # If the BUILD file contains external packages, add the Bazel method for installing them.
    if 'requirement("' in build_source:
        requirement = REQUIREMENT
    else:
        requirement = ''

    header = HEADER.format(requirement=requirement)
    build_source = header + build_source

    with open(os.path.join(directory, 'BUILD'), 'w') as f:
        f.write(build_source)


def app(input_path, project_root, pre_installed_packages):
    """Generate BUILD file(s) for a Python script or a directory of Python scripts."""

    # Handle directories.
    if os.path.isdir(input_path):
        # Traverse the directory recursively.
        for dirpath, _, filenames in os.walk(input_path):
            build_source = ''

            for filename in sorted(filenames):
                path = os.path.join(dirpath, filename)

                # Generate rule for Python files.
                if is_valid_python_file(path):
                    build_source += parse_script_and_generate_rule(path, project_root,
                                                                   pre_installed_packages)
                    build_source += 2*'\n'  # newline between rules.

            if build_source != '':
                output_build_file(build_source, dirpath)
    # Handle single Python files.
    elif is_valid_python_file(input_path):
        build_source = parse_script_and_generate_rule(input_path, project_root,
                                                      pre_installed_packages)

        output_build_file(build_source, os.path.dirpath(input_path))
    else:
        raise RuntimeError("Invalid input path %s." % input_path)


def main():
    """Parse command-line flags and generate the BUILD files accordingly."""
    parser = argparse.ArgumentParser(description='Generate Bazel BUILD files for a Python project.')

    parser.add_argument('input_path', nargs='?', type=str, default=os.getcwd(),
                        help='Target Python file or directory of Python files.'
                        ' Defaults to the current working directory.')
    parser.add_argument('-r', '--project-root', type=str, default=os.getcwd(),
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