"""Test identifying Bazel rule type of a script and generating new rules to BUILD files."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

from pazel.generate_rule import infer_bazel_rule_types
from pazel.bazel_rules import BazelRule
from pazel.languages.py.py_rules import get_bazel_rules
from pazel.languages.py.py_rules import PyBinaryRule
from pazel.languages.py.py_rules import PY_BINARY_TEMPLATE
from pazel.languages.py.py_rules import PyLibraryRule
from pazel.languages.py.py_rules import PY_LIBRARY_TEMPLATE
from pazel.languages.py.py_rules import PyTestRule
from pazel.languages.py.py_rules import PY_TEST_TEMPLATE


class TestTemplates(unittest.TestCase):
    """Test filling different Bazel rule templates."""

    @staticmethod
    def _format_generated(generated):
        return "\n".join([g for g in generated.splitlines() if g.strip()])

    def test_py_binary_template(self):
        """Test PY_BINARY_TEMPLATE."""
        name = 'my'
        data = 'data = ["something"],'
        deps = "deps = ['//foo:bar']"

        expected = """py_binary(
    name = "my",
    srcs = ["my.py"],
    data = ["something"],
    deps = ['//foo:bar']
)"""

        # Generate the rule and strip empty lines.
        generated = PY_BINARY_TEMPLATE.format(name=name, data=data, deps=deps)
        generated = self._format_generated(generated)

        self.assertEqual(generated, expected)

    def test_py_library_template(self):
        """Test PY_LIBRARY_TEMPLATE."""
        name = 'my'
        data = ''   # Empty 'data' should be stripped away.
        deps = "deps = ['//foo:bar']"

        expected = """py_library(
    name = "my",
    srcs = ["my.py"],
    deps = ['//foo:bar']
)"""

        # Generate the rule and strip empty lines.
        generated = PY_LIBRARY_TEMPLATE.format(name=name, data=data, deps=deps)
        generated = self._format_generated(generated)

        self.assertEqual(generated, expected)

    def test_py_test_template(self):
        """Test PY_TEST_TEMPLATE."""
        name = 'my_test'
        size = 'medium'
        data = 'data = ["something"],'
        deps = "deps = ['//foo:bar']"

        expected = """py_test(
    name = "my_test",
    srcs = ["my_test.py"],
    size = "medium",
    data = ["something"],
    deps = ['//foo:bar']
)"""

        # Generate the rule and strip empty lines.
        generated = PY_TEST_TEMPLATE.format(name=name, size=size, data=data, deps=deps)
        generated = self._format_generated(generated)

        self.assertEqual(generated, expected)


# Define a few different script sources.
# pylint: disable=invalid-name
script_name = 'my.py'
test_script_name = 'test_my.py'

module_source = """
import time

def myfunction():
    pass
"""

binary_with_main_source = """
def main():
    pass

if __name__ == "__main__":
    main()
"""

binary_without_main_source = """
def myfunction():
    pass

myfunction()
"""

test_source = """
import unittest

class TestPyBinaryRule(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
"""


class TestPyBinaryRule(unittest.TestCase):
    """Test PyBinaryRule."""

    def test_class_variables(self):
        """Test class variables of the PyBinaryRule class."""
        self.assertEqual(PyBinaryRule.is_test_rule, False)
        self.assertEqual(PyBinaryRule.template, PY_BINARY_TEMPLATE)
        self.assertEqual(PyBinaryRule.rule_identifier, 'py_binary')

    def test_applies_to(self):
        """Test PyBinaryRule.applies_to for different script sources."""
        # A script containing __main__ should generate a py_binary rule.
        self.assertEqual(PyBinaryRule.applies_to(script_name, binary_with_main_source), True)

        # Ditto for a level 0 function call.
        self.assertEqual(PyBinaryRule.applies_to(script_name, binary_without_main_source), True)

        # Modules should not generate a py_binary rule.
        self.assertEqual(PyBinaryRule.applies_to(script_name, module_source), False)

        # Tests should not generate a py_binary rule even though they contain __main__.
        self.assertEqual(PyBinaryRule.applies_to(test_script_name, test_source), False)


class TestPyLibraryRule(unittest.TestCase):
    """Test PyLibraryRule."""

    def test_class_variables(self):
        """Test class variables of the PyLibraryRule class."""
        self.assertEqual(PyLibraryRule.is_test_rule, False)
        self.assertEqual(PyLibraryRule.template, PY_LIBRARY_TEMPLATE)
        self.assertEqual(PyLibraryRule.rule_identifier, 'py_library')

    def test_applies_to(self):
        """Test PyLibraryRule.applies_to for different script sources."""
        self.assertEqual(PyLibraryRule.applies_to(script_name, binary_with_main_source), False)
        self.assertEqual(PyLibraryRule.applies_to(script_name, binary_without_main_source), False)
        self.assertEqual(PyLibraryRule.applies_to(script_name, module_source), True)
        self.assertEqual(PyLibraryRule.applies_to(test_script_name, test_source), False)


class TestPyTestRule(unittest.TestCase):
    """Test PyTestRule."""

    def test_class_variables(self):
        """Test class variables of the PyTestRule class."""
        self.assertEqual(PyTestRule.is_test_rule, True)
        self.assertEqual(PyTestRule.template, PY_TEST_TEMPLATE)
        self.assertEqual(PyTestRule.rule_identifier, 'py_test')

    def test_applies_to(self):
        """Test PyTestRule.applies_to for different script sources."""
        self.assertEqual(PyTestRule.applies_to(script_name, binary_with_main_source), False)
        self.assertEqual(PyTestRule.applies_to(script_name, binary_without_main_source), False)
        self.assertEqual(PyTestRule.applies_to(script_name, module_source), False)
        self.assertEqual(PyTestRule.applies_to(test_script_name, test_source), True)


class TestGetBazelRules(unittest.TestCase):
    """Test getting native Bazel rule classes."""

    def test_get_bazel_rules(self):
        """Test getting the list of native Bazel rules."""
        native_rules = set([PyBinaryRule, PyLibraryRule, PyTestRule])
        self.assertEqual(set(get_bazel_rules()), native_rules)


class TestBazelRuleInference(unittest.TestCase):
    """Test inferring the Bazel rule type of a script."""

    def test_infer_bazel_rule_type(self):
        """Test inferring the Bazel rule type."""
        custom_rules = []

        self.assertEqual(infer_bazel_rule_types(script_name, binary_with_main_source, custom_rules),
                         [PyBinaryRule])
        self.assertEqual(infer_bazel_rule_types(script_name, binary_without_main_source,
                                               custom_rules), [PyBinaryRule])
        self.assertEqual(infer_bazel_rule_types(script_name, module_source, custom_rules),
                         [PyLibraryRule])
        self.assertEqual(infer_bazel_rule_types(test_script_name, test_source, custom_rules),
                         [PyTestRule])


if __name__ == '__main__':
    unittest.main()
