"""Generate Bazel rule for a single Python file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from pazel.helpers import contains_py_files
from pazel.helpers import is_installed

from pazel.parse_build import find_existing_data_deps
from pazel.parse_build import find_existing_rule
from pazel.parse_build import find_existing_test_size
from pazel.parse_build import infer_python_rule_type

from pazel.parse_imports import get_imports
from pazel.parse_imports import infer_import_type

from pazel.script_type import ScriptType


# For some packages, the import name differs from that of the pip package...
IMPORT_NAME_TO_PIP_NAME = {'cv2': 'opencv-python', 'yaml': 'pyyaml'}

PY_BINARY_TEMPLATE = """py_binary(
    name = "{name}",
    srcs = ["{name}.py"],
    deps = [{deps}],
    {data}
)"""

PY_LIBRARY_TEMPLATE = """py_library(
    name = "{name}",
    srcs = ["{name}.py"],
    deps = [{deps}],
    {data}
)"""

PY_TEST_TEMPLATE = """py_test(
    name = "{name}",
    srcs = ["{name}.py"],
    size = "{size}",
    deps = [{deps}],
    {data}
)"""


def generate_rule(script_path, script_type, package_names, module_names, data_deps, test_size):
    """Generate a Bazel Python rule given the type of the Python file and imports in it."""
    if script_type == ScriptType.BINARY:
        template = PY_BINARY_TEMPLATE
    elif script_type == ScriptType.LIBRARY:
        template = PY_LIBRARY_TEMPLATE
    elif script_type == ScriptType.TEST:
        template = PY_TEST_TEMPLATE

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

    for module_name in sorted(list(set(module_names))):
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
    package_names = [p.split('.')[0] for p in package_names]

    for package_name in sorted(list(set(package_names))):
        if multiple_deps:
            deps += 2*tab

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


def parse_script_and_generate_rule(script_path, project_root, pre_installed_packages):
    """Generate Bazel Python rule for a Python script."""
    with open(script_path, 'r') as f:
        source = f.read()

    # Get all imports in the current script.
    package_names, from_imports = get_imports(source)
    all_imports = package_names + from_imports

    # Infer the import type: Is a package, module, or an object being imported.
    package_names, module_names = infer_import_type(all_imports, project_root,
                                                    pre_installed_packages)

    # Infer the script type: library, binary or test.
    script_type = infer_python_rule_type(script_path, source)

    # Data dependencies or test size cannot be inferred currently.
    # Use information in any existing BUILD files.
    data_deps = find_existing_data_deps(script_path, script_type)
    test_size = find_existing_test_size(script_path) if script_type == ScriptType.TEST else None

    # Generate the Bazel Python rule based on the gathered information.
    rule = generate_rule(script_path, script_type, package_names, module_names, data_deps,
                         test_size)

    return rule
