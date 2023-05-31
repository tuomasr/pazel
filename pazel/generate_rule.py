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


def _walk_modules(current_dir, modules):
    """Walk modules in different directories.

    This function is similar to os.walk but it returns module names in a sorted order.

    Args:
        current_dir (str): Current directory that contains one or many modules.
        modules (list of str): List of modules in current_dir or in its subdirectories.

    Yields:
        sorted list of module names in a directory.
    """
    modules_in_current_dir, remaining_modules, subdirs = [], [], []

    for module in modules:
        # Map e.g. "foo.abc" and "foo.abc.xyz" to "abc" and "abc.xyz", respectively.
        remaining_module_name = module.replace(current_dir, '').split('.')

        is_in_current_dir = len(remaining_module_name) == 1

        if is_in_current_dir:
            modules_in_current_dir.append(module)
        else:
            remaining_modules.append(module)
            subdirs.append(remaining_module_name[0])

    # Modules in the current directory precede modules in subdirectories.
    yield sorted(modules_in_current_dir)

    # Recurse modules in subdirectories.
    sorted_subdirs = sorted(list(set(subdirs)))

    for subdir in sorted_subdirs:
        next_dir = current_dir + subdir + '.' if current_dir else subdir + '.'
        # Consider only modules in the current subdirectory.
        remaining_modules_in_next_dir = [module for module in remaining_modules if
                                         next_dir in module]

        for x in _walk_modules(next_dir, remaining_modules_in_next_dir):
            yield x


def sort_module_names(module_names):
    """Sort modules alphabetically but so that modules in a directory precede modules in subdirs.

    For example, modules ["xyz", "abc", "foo.bar1"] are sorted to ["abc", "xyz", "foo.bar1"].

    Args:
        module_names (list of str): List of module names in dotted notation ("foo.bar.xyz").

    Returns:
        sorted_modules_names (list of str): List of sorted module names.
    """
    sorted_module_names = []

    for module_name in _walk_modules('', module_names):
        sorted_module_names += module_name

    return sorted_module_names


def generate_rule(script_path, template, package_names, module_names, data_deps, test_size,
                  import_name_to_pip_name, local_import_name_to_dep):
    """Generate a Bazel Python rule given the type of the Python file and imports in it.

    Args:
        script_path (str): Path to a Python script.
        template (str): Template for writing a Bazel rule. To be filled with name, srcs, deps, etc.
        package_names (set of str): Set of imported packages names in dotted notation (pkg1.pkg2).
        module_names (set of str): Set of imported module names in dotted notation (pkg.module)
        data_deps (str): Data dependencies parsed from an existing BUILD file.
        test_size (str): Test size parsed from an existing BUILD file.
        import_name_to_pip_name (dict): Mapping from Python package import name to its pip name.
        local_import_name_to_dep (dict): Mapping from local package import name to its Bazel
            dependency.

    Returns:
        rule (str): Bazel rule generated for the current Python script.
    """
    script_name = os.path.basename(os.path.splitext(script_path)[0])
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

    for module_name in sort_module_names(list(module_names)):
        module_name = translate_dot_module_name_to_bazel(module_name)

        if multiple_deps:
            deps += 2*tab

        deps += '\"' + module_name + '\"'

        if multiple_deps:
            deps += ',\n'

    # Even if a submodule of a local or external package is required, install the whole package.
    package_names = set([p.split('.')[0] for p in package_names])

    # Split packages to local and external.
    local_packages = [p for p in package_names if p in local_import_name_to_dep]
    external_packages = [p for p in package_names if p not in local_import_name_to_dep]

    for package_set in (local_packages, external_packages):     # List local packages first.
        for package_name in sorted(list(package_set)):
            if multiple_deps:
                deps += 2*tab

            if package_name in local_import_name_to_dep:    # Local package.
                package_name = local_import_name_to_dep[package_name]
                deps += '\"' + package_name + '\"'
            else:   # External/pip installable package.
                package_name = import_name_to_pip_name.get(package_name, package_name)
                package_name = 'requirement(\"%s\")' % package_name
                deps += package_name

            if multiple_deps:
                deps += ',\n'

    if multiple_deps:
        deps += tab

    if deps:
        deps = 'deps = [{deps}],'.format(deps=deps)

    data = data_deps + ',' if data_deps is not None else ''
    size = test_size if test_size is not None else 'small'  # If size not given, assume small.

    rule = template.format(name=script_name, deps=deps, data=data, size=size)
    # If e.g. 'data' is missing, then remove blank lines.
    rule = "\n".join([s for s in rule.splitlines() if s.strip()])

    return rule

def translate_dot_module_name_to_bazel(module_name):
    if '.' not in module_name:
            # Import from the same directory as the script resides.
            module_name = ':' + module_name
    else:
        # Interpret dot separated path as a bazel rule path.
        module_components = module_name.split('.')

        # Pull out external repository name before creating root path.
        # See: https://bazel.build/extending/repo
        external_repository = ''
        if module_components[0].startswith('@'):
            external_repository = module_components.pop(0)

        # Format the dotted module name to the Bazel format with slashes.
        module_name = external_repository + '//'
        if len(module_components) == 1:
            module_name = module_name + ':' + module_components[0]
        else:
            module_name = module_name + '/'.join(module_components[:-1])
            if len(module_components) > 1 and (module_components[-2] != module_components[-1]):
                module_name = module_name + ':' + module_components[-1]
    return module_name

def parse_script_and_generate_rule(script_path, project_root, contains_pre_installed_packages,
                                   custom_bazel_rules, custom_import_inference_rules,
                                   import_name_to_pip_name, local_import_name_to_dep):
    """Generate Bazel Python rule for a Python script.

    Args:
        script_path (str): Path to a file for which the Bazel rule is generated.  Usually Python,
            but could be an extra extension type requested by for custom rules.
        project_root (str): Imports in the Python script are assumed to be relative to this path.
        contains_pre_installed_packages (bool): Environment contains pre-installed packages (true)
            or only the standard library (false).
        custom_bazel_rules (list of BazelRule classes): Custom rule classes implementing BazelRule.
        custom_import_inference_rules (list of ImportInferenceRule classes): Custom rule classes
            implementing ImportInferenceRule.
        import_name_to_pip_name (dict): Mapping from Python package import name to its pip name.
        local_import_name_to_dep (dict): Mapping from local package import name to its Bazel
            dependency.

    Returns:
        rule (str): Bazel rule generated for the Python script.
    """
    with open(script_path, 'r') as script_file:
        script_source = script_file.read()

    # Get all imports in the script.
    package_names = []
    from_imports = []
    if script_path.endswith('.py'):
        package_names, from_imports = get_imports(script_source)
    all_imports = package_names + from_imports

    # Infer the import type: Is a package, module, or an object being imported.
    package_names, module_names = infer_import_type(all_imports, project_root,
                                                    contains_pre_installed_packages,
                                                    custom_import_inference_rules)

    # Infer the Bazel rule type for the script.
    bazel_rule_type = infer_bazel_rule_type(script_path, script_source, custom_bazel_rules)

    # Data dependencies or test size cannot be inferred from the script source code currently.
    # Use information in any existing BUILD files.
    data_deps = find_existing_data_deps(script_path, bazel_rule_type)
    test_size = find_existing_test_size(script_path, bazel_rule_type)

    # Generate the Bazel Python rule based on the gathered information.
    rule = generate_rule(script_path, bazel_rule_type.template, package_names, module_names,
                         data_deps, test_size, import_name_to_pip_name, local_import_name_to_dep)

    return rule
