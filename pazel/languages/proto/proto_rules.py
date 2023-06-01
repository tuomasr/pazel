"""Classes for identifying Bazel rule type of a Protobuffer definition and generating new rules to BUILD files."""

from pazel.bazel_rules import BazelRule


# These templates will be filled and used to generate BUILD files.
# Note that both 'data' and 'deps' can be empty in which case they are left out from the rules.
PROTO_LIBRARY_TEMPLATE = """proto_library(
    name = "{name}_proto",
    srcs = ["{name}.proto"],
    {data}
    {deps}
)
"""

PY_PROTO_LIBRARY_TEMPLATE = """
py_proto_library(
    name = "{name}_py_pb2",
    deps = [":{name}_proto"],
)
"""

class ProtoLibraryRule(BazelRule):
    is_test_rule = False
    template = PROTO_LIBRARY_TEMPLATE
    rule_identifier = 'proto_library'

    @staticmethod
    def applies_to(script_name, script_source):
        # TODO(gobeil): Scan source for proto syntax statement.
        return True

    @staticmethod
    def get_load_statement():
        return 'load("@rules_proto//proto:defs.bzl", "proto_library")'

class PyProtoLibraryRule(BazelRule):
    is_test_rule = False
    template = PY_PROTO_LIBRARY_TEMPLATE
    rule_identifier = 'py_proto_library'

    @staticmethod
    def applies_to(script_name, script_source):
        # TODO(gobeil): Scan source for proto syntax statement.
        # TODO(gobeil): Scan source for python generation annotation?
        return True

    @staticmethod
    def get_load_statement():
        return 'load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")'

def get_bazel_rules():
    """Return a copy of the pazel-native classes implementing BazelRule."""
    return [ProtoLibraryRule, PyProtoLibraryRule]
