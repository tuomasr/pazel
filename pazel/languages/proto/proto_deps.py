"""Parse imports in Proto files and infer what is being imported."""

import re


def get_imports(script_source):
    """Parse imported packages.

    Args:
        script_source (str): The source code of a Proto definition.

    Returns:
        packages (list of tuple): List of (package name, None) tuples.
        from_imports (list of tuple): List of (package/module name, some object) tuples.
    """
    packages = []
    from_imports = []

    # TODO(gobeil): Ignore imports on commented lines.
    import_matches = re.findall('(.*)import "(.*)\.proto"', script_source, re.MULTILINE)
    for pre_match, import_match in import_matches:
        # Ignore commented lines
        if '//' in pre_match:
            continue
        # Convert to dot notation with "_proto" postfix convention.
        components = import_match.split('/')
        from_imports.append(('.'.join(components[:-1]), components[-1] + '_proto'))

    return packages, from_imports

def infer_import_type(all_imports, project_root, contains_pre_installed_packages, custom_rules):
    packages = []
    modules = []

    for base, unknown in all_imports:
        # TODO(gobeil): Abstract this out to share with python language copy as boilerplate.
        custom_rule_matches = False
        for inference_rule in custom_rules:
            new_packages, new_modules = inference_rule.holds(project_root, base, unknown)

            # If the rule holds, then add to the list of packages and/or modules.
            if new_packages is not None:
                packages.extend(new_packages)

            if new_modules is not None:
                modules.extend(new_modules)

            if new_packages is not None or new_modules is not None:
                custom_rule_matches = True  # Only allow one match for custom rules.
                break

        if custom_rule_matches:
            continue

        dotted_path = base + '.%s' % unknown
        modules.append(dotted_path)

    return set(packages), set(modules)
