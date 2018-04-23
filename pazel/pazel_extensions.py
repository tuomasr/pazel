"""Handle user-defined pazel extensions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast
import imp
import os

from pazel.bazel_rules import REGISTERED_RULES  # noqa
from pazel.generate_rule import IMPORT_NAME_TO_PIP_NAME     # noqa
from pazel.generate_rule import LOCAL_IMPORT_NAME_TO_DEP    # noqa


PAZELRC_FILE = '.pazelrc'


class OutputExtension(object):
    """A class representing pazel extension to outputting BUILD files."""

    def __init__(self, header, footer):
        """Instantiate.

        Args:
            header (str): Header for BUILD files.
            footer (str): Footer for BUILD files.
        """
        self.header = header
        self.footer = footer


def parse_pazel_extensions(directory):
    """Parse pazel extensions from a .pazelrc file.

    Parses user-defined header and footer as well as updates the list of registered rule classes
    that pazel uses to generate Bazel rules for Python scripts. See the main README.md for
    instructions for programming pazel.

    Args:
        directory (str): Path to a directory that may contain a .pazelrc file.

    Returns:
        output_extension (OutputExtension): Object containing user-defined header and footer.

    Raises:
        SyntaxError: If the .pazelrc contains invalid Python syntax.
    """
    pazelrc_path = os.path.join(directory, PAZELRC_FILE)

    header = ''
    footer = ''

    # Try parsing the .pazelrc to check that it contains valid Python syntax.
    try:
        with open(pazelrc_path, 'r') as pazelrc_file:
            pazelrc_source = pazelrc_file.read()
            ast.parse(pazelrc_source)
    except IOError:
        return OutputExtension(header, footer)
    except SyntaxError:
        raise SyntaxError("Invalid syntax in %s. Run the file with an interpreter." % pazelrc_path)

    pazelrc = imp.load_source('pazelrc', pazelrc_path)

    # Read user-defined header and footer.
    header = getattr(pazelrc, 'HEADER', '')
    footer = getattr(pazelrc, 'FOOTER', '')

    output_extension = OutputExtension(header, footer)

    # Read user-defined pazel Rule classes.
    user_defined_bazel_rules = getattr(pazelrc, 'EXTRA_RULES', [])

    # Update the list of registered rules. TODO: Remove global.
    global REGISTERED_RULES
    REGISTERED_RULES += user_defined_bazel_rules

    # Read user-defined mapping from package import names to pip package names.
    user_defined_pip_import_mapping = getattr(pazelrc, 'EXTRA_IMPORT_NAME_TO_PIP_NAME', dict())

    # Update the corresponding mapping. TODO: Remove global.
    global IMPORT_NAME_TO_PIP_NAME
    IMPORT_NAME_TO_PIP_NAME.update(user_defined_pip_import_mapping)

    # Read user-defined mapping from local import names to their Bazel dependencies.
    user_defined_local_dep_mapping = getattr(pazelrc, 'EXTRA_LOCAL_IMPORT_NAME_TO_DEP', dict())

    # Update the corresponding mapping. TODO: Remove global.
    global LOCAL_IMPORT_NAME_TO_DEP
    LOCAL_IMPORT_NAME_TO_DEP.update(user_defined_local_dep_mapping)

    return output_extension
