"""Handle user-defined pazel extensions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast
import os


PAZELRC_FILE = '.pazelrc'


class PazelExtension(object):
    """A class representing pazel extensions."""

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

    Args:
        directory (str): Path to a directory that may contain a .pazelrc file.

    Returns:
        extension (PazelExtension): Object containing user-defined extensions.

    Raises:
        SyntaxError: If the .pazelrc contains invalid Python syntax.
    """
    pazelrc_path = os.path.join(directory, PAZELRC_FILE)

    header = ''
    footer = ''

    try:
        with open(pazelrc_path, 'r') as pazelrc:
            pazel_extensions_source = pazelrc.read()
    except IOError:
        return PazelExtension(header, footer)

    try:
        top_node = ast.parse(pazel_extensions_source)
    except SyntaxError:
        raise SyntaxError("Invalid syntax in %s." % pazelrc_path)

    for node in top_node.body:
        # Check assigning to 'HEADER' and 'FOOTER'.
        if isinstance(node, ast.Assign):
            # The number of variables on the left side should be 1.
            if len(node.targets) == 1:
                left_side = node.targets[0].id

                if left_side == 'HEADER':
                    header = node.value.s
                elif left_side == 'FOOTER':
                    footer = node.value.s

    extension = PazelExtension(header, footer)

    return extension
