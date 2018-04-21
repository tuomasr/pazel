"""Output a BUILD file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os


# Used for installing pip packages. See https://github.com/bazelbuild/rules_python
REQUIREMENT = """
load("@my_deps//:requirements.bzl", "requirement")"""

HEADER = """package(default_visibility = ["//visibility:public"]){requirement}

"""


def output_build_file(build_source, directory):
    """Output a BUILD file.

    Args:
        build_source (str): The contents of the BUILD file to output.
        directory (str): The directory in which the BUILD file is stored.
    """
    # If the BUILD file contains external packages, add the Bazel method for installing them.
    if 'requirement("' in build_source:
        requirement = REQUIREMENT
    else:
        requirement = ''

    header = HEADER.format(requirement=requirement)
    build_source = header + build_source

    with open(os.path.join(directory, 'BUILD'), 'w') as build_file:
        build_file.write(build_source)
