"""Parse imports in Python files and infer what is being imported from which package."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast
import os

from pazel.helpers import is_installed


def get_imports(source):
    """Get a list of tuples (package/module name, function/object/module/package name)."""
    packages = []
    from_imports = []
    ast_of_source = ast.parse(source)

    for node in ast_of_source.body:
        if isinstance(node, ast.ImportFrom):
            module = node.module

            for name in node.names:
                from_imports.append((module, name.name))
        elif isinstance(node, ast.Import):
            for package in node.names:
                packages.append((package.name, None))

    return packages, from_imports


def infer_import_type(all_imports, project_root, pre_installed_packages):
    """Infer what is being imported.

    Given a list of tuples (package/module, some object) infer whether the first element is a
    package or a module and whether it is installed. Also, infer the type of the second element.
    """
    modules = []
    packages = []

    for base, unknown in all_imports:
        # Early exit if base is in the installed modules of the current environment.
        if is_installed(base, unknown, pre_installed_packages):
            continue

        # By default, assume that 'base' is a module and 'unknown' is function, variable or any
        # other object in that module.
        module_path = os.path.join(project_root, base.replace('.', '/') + '.py')
        if os.path.exists(module_path):
            modules.append(base)
            continue

        # Check if 'unknown' is actually a package or a module.
        dotted_path = base + '.%s' % unknown
        package_path = os.path.join(project_root, dotted_path.replace('.', '/'))
        module_path = os.path.join(project_root, dotted_path.replace('.', '/') + '.py')

        unknown_is_package = os.path.isdir(package_path) and contains_py_files(package_path)
        unknown_is_module = os.path.isfile(module_path)

        if unknown_is_package:
            # Assume that for package //foo, there exists rule //foo:foo.
            dotted_path += '.%s' % unknown
            modules.append(dotted_path)
            continue

        if unknown_is_module:
            modules.append(dotted_path)
            continue

        # Finally, assume that base is either a pip installable or a local package.
        packages.append(base)

    return set(packages), set(modules)
