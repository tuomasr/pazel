"""Interface for defining custom classes for inferring import type."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class ImportInferenceRule(object):
    """Base class defining the interface for custom import inference classes.

    Custom classes define how a Python import is mapped to Bazel dependencies.
    """

    @staticmethod
    def holds(project_root, base, unknown):
        """If this import inference rule holds, then return imported packages and/or modules.

        Args:
            project_root (str): Local imports are assumed to be relative to this path.
            base (str): Name of a package or a module.
            unknown (str): Can package, module, function or any other object.

        Returns:
            packages (list of str or None): Imported package names. None if no packages are imported
                or if the rule does not match the import.
            modules (list of str or None): Imported module names. None if no modules are imported or
                if the rule does not match the import.
        """
        raise NotImplementedError()
