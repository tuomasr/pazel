"""Generate Bazel rule for a single Python file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from pazel.bazel_rules import infer_bazel_rule_type
from pazel.parse_build import find_existing_data_deps
from pazel.parse_build import find_existing_test_size
from pazel.parse_imports import get_imports
from pazel.parse_imports import infer_import_type


# Map external package import name to pip installation name ({'yaml': 'pyyaml'}, for example).
IMPORT_NAME_TO_PIP_NAME = {}
# Map local package import name to Bazel dependency name ({'mypackage': '//mypackage'}).
LOCAL_IMPORT_NAME_TO_DEP = {}


def generate_rule(script_path, template, package_names, module_names, data_deps, test_size):
    """Generate a Bazel Python rule given the type of the Python file and imports in it.

    Args:
        script_path (str): Path to a Python script.
        template (str): Template for writing a Bazel rule. To be filled with name, srcs, deps, etc.
        package_names (set of str): Set of imported packages names in dotted notation (pkg1.pkg2).
        module_names (set of str): Set of imported module names in dotted notation (pkg.module)
        data_deps (str): Data dependencies parsed from an existing BUILD file.
        test_size (str): Test size parsed from an existing BUILD file.

    Returns:
        rule (str): Bazel rule generated for the current Python script.
    """
    script_name = os.path.basename(script_path).replace('.py', '')
    deps = ''
    tab = '    '

    num_deps = len(module_names) + len(package_names)
    multiple_deps = num_deps > 1

    # Formatting with one dependency:
    # deps = ["//my_dep1/foo:abc"]
    # Formatting with multiple dependencies:
    # deps = [
    #       "//my_dep1/foo:abc",
    #       "//my_dep2/bar:xyz",
    #   ]

    if multiple_deps:
        deps += '\n'

    for module_name in sorted(list(module_names)):
        if '.' not in module_name:
            module_name = ':' + module_name
        else:
            # Format the dotted module name to the Bazel format with slashes.
            module_name = '//' + module_name.replace('.', '/')

            # Replace the last slash with :.
            last_slash_idx = module_name.rfind('/')
            module_name = module_name[:last_slash_idx] + ':' + module_name[last_slash_idx + 1:]

        if multiple_deps:
            deps += 2*tab

        deps += '\"' + module_name + '\"'

        if multiple_deps:
            deps += ',\n'

    # Even if a submodule of a local or external package is required, install the whole package.
    package_names = set([p.split('.')[0] for p in package_names])

    # Split packages to local and external.
    local_packages = [p for p in package_names if p in LOCAL_IMPORT_NAME_TO_DEP]
    external_packages = [p for p in package_names if p not in LOCAL_IMPORT_NAME_TO_DEP]

    for package_set in (local_packages, external_packages):     # List local packages first.
        for package_name in sorted(list(package_set)):
            if multiple_deps:
                deps += 2*tab

            if package_name in LOCAL_IMPORT_NAME_TO_DEP:    # Local package.
                package_name = LOCAL_IMPORT_NAME_TO_DEP[package_name]
                deps += '\"' + package_name + '\"'
            else:   # External/pip installable package.
                package_name = IMPORT_NAME_TO_PIP_NAME.get(package_name, package_name)
                package_name = 'requirement(\"%s\")' % package_name
                deps += package_name

            if multiple_deps:
                deps += ',\n'

    if multiple_deps:
        deps += tab

    data = data_deps if data_deps is not None else ''
    size = test_size if test_size is not None else 'small'  # If size not given, assume small.

    rule = template.format(name=script_name, deps=deps, data=data, size=size)
    # If e.g. 'data' is missing, then remove blank lines.
    rule = "\n".join([s for s in rule.splitlines() if s.strip()])

    return rule


def parse_script_and_generate_rule(script_path, project_root, contains_pre_installed_packages):
    """Generate Bazel Python rule for a Python script.

    Args:
        script_path (str): Path to a Python file for which the Bazel rule is generated.
        project_root (str): Imports in the Python script are assumed to be relative to this path.
        contains_pre_installed_packages (bool): Environment contains pre-installed packages (true)
        or only the standard library (false).

    Returns:
        rule (str): Bazel rule generated for the Python script.
    """
    with open(script_path, 'r') as script_file:
        script_source = script_file.read()

    # Get all imports in the script.
    package_names, from_imports = get_imports(script_source)
    all_imports = package_names + from_imports

    # Infer the import type: Is a package, module, or an object being imported.
    package_names, module_names = infer_import_type(all_imports, project_root,
                                                    contains_pre_installed_packages)

    # Infer the Bazel rule type for the script.
    bazel_rule_type = infer_bazel_rule_type(script_path, script_source)

    # Data dependencies or test size cannot be inferred from the script source code currently.
    # Use information in any existing BUILD files.
    data_deps = find_existing_data_deps(script_path, bazel_rule_type)
    test_size = find_existing_test_size(script_path, bazel_rule_type)

    # Generate the Bazel Python rule based on the gathered information.
    rule = generate_rule(script_path, bazel_rule_type.template, package_names, module_names,
                         data_deps, test_size)

    return rule
