"""Handle user-defined pazel extensions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast
import imp


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


def parse_pazel_extensions(pazelrc_path):
    """Parse pazel extensions from a .pazelrc file.

    Parses user-defined header and footer as well as updates the list of registered rule classes
    that pazel uses to generate Bazel rules for Python scripts. See the main README.md for
    instructions for programming pazel.

    Args:
        pazelrc_path (str): Path to .pazelrc config file for customizing pazel.

    Returns:
        output_extension (OutputExtension): Object containing user-defined header and footer.
        custom_bazel_rules (list of BazelRule classes): Custom BazelRule classes.
        custom_bazel_rules_extra_extensions: Extra filename extensions to allow custom_bazel_rules
            implementations to visit (e.g. .proto) as rules based on them may generate python code.
        custom_import_inference_rules (list of ImportInferenceRule classes): Custom classes
            for inferring import types.
        import_name_to_pip_name (dict): Mapping from Python package import name to its pip name.
        local_import_name_to_dep (dict): Mapping from local package import name to its Bazel
            dependency.
        requirement_load (str): Statement for loading the 'requirement' rule for installing pip
            packages.

    Raises:
        SyntaxError: If the .pazelrc contains invalid Python syntax.
    """
    # Try parsing the .pazelrc to check that it contains valid Python syntax.
    try:
        with open(pazelrc_path, 'r') as pazelrc_file:
            pazelrc_source = pazelrc_file.read()
            ast.parse(pazelrc_source)

        pazelrc = imp.load_source('pazelrc', pazelrc_path)
    except IOError:
        # The file does not exist. Use a dummy pazelrc that contains nothing.
        pazelrc = dict()
    except SyntaxError:
        raise SyntaxError("Invalid syntax in %s. Run the file with an interpreter." % pazelrc_path)

    # Read user-defined header and footer.
    header = getattr(pazelrc, 'HEADER', '')
    footer = getattr(pazelrc, 'FOOTER', '')

    assert isinstance(header, str), "HEADER must be a string."
    assert isinstance(footer, str), "FOOTER must be a string."

    output_extension = OutputExtension(header, footer)

    # Read user-defined BazelRule classes.
    custom_bazel_rules = getattr(pazelrc, 'EXTRA_BAZEL_RULES', [])
    assert isinstance(custom_bazel_rules, list), "EXTRA_BAZEL_RULES must be a list."

    custom_bazel_rules_extra_extensions = getattr(pazelrc, 'EXTRA_BAZEL_RULES_FILE_EXTENSIONS', [])
    assert isinstance(custom_bazel_rules_extra_extensions, list), "EXTRA_BAZEL_RULES_FILE_EXTENSIONS must be a list."

    # Read user-defined ImportInferenceRule classes.
    custom_import_inference_rules = getattr(pazelrc, 'EXTRA_IMPORT_INFERENCE_RULES', [])
    assert isinstance(custom_import_inference_rules, list), \
        "EXTRA_IMPORT_INFERENCE_RULES must be a list."

    # Read user-defined mapping from package import names to pip package names.
    import_name_to_pip_name = getattr(pazelrc, 'EXTRA_IMPORT_NAME_TO_PIP_NAME', dict())
    assert isinstance(import_name_to_pip_name, dict), \
        "EXTRA_IMPORT_NAME_TO_PIP_NAME must be a dictionary."

    # Read user-defined mapping from local import names to their Bazel dependencies.
    local_import_name_to_dep = getattr(pazelrc, 'EXTRA_LOCAL_IMPORT_NAME_TO_DEP', dict())
    assert isinstance(local_import_name_to_dep, dict), \
        "EXTRA_LOCAL_IMPORT_NAME_TO_DEP must be a dictionary."

    default_requirement_load = 'load("@my_deps//:requirements.bzl", "requirement")'
    requirement_load = getattr(pazelrc, 'REQUIREMENT', default_requirement_load)

    assert isinstance(requirement_load, str), "REQUIREMENT must be a string."

    return output_extension, custom_bazel_rules, custom_bazel_rules_extra_extensions, \
        custom_import_inference_rules, import_name_to_pip_name, local_import_name_to_dep, \
        requirement_load
