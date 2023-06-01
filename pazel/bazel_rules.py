import re

class BazelRule(object):
    """Base class defining the interface for parsing Bazel rules.

    pazel-native rule classes as well as custom rule classes need to implement this interface.
    """

    # Required class variables.
    is_test_rule = None
    template = None
    rule_identifier = None
    replaces_rules = []

    @staticmethod
    def applies_to(script_name, script_source):
        """Check whether this rule applies to a given script.

        Args:
            script_name (str): Name of a Python script without the file extension suffix.
            script_source (str): Source code of the script.

        Returns:
            applies (bool): Whether this Bazel rule can be used to represent the script.
        """
        raise NotImplementedError()

    @staticmethod
    def find_existing(build_source, script_filename):
        """Find existing rule for a given script.

        Args:
            build_source (str): Source code of an existing BUILD file.
            script_filename (str): Name of a Python script.

        Returns:
            match (MatchObject or None): Match found in the BUILD file or None if no matches.
        """
        # 'srcs' should contain the script filename.
        pattern = 'srcs\s*=\s*\["' + script_filename + '"\]'
        match = re.search(pattern, build_source)

        return match

    @staticmethod
    def get_load_statement():
        """If the rule requires a special 'load' statement, return it, otherwise return None."""
        return None
