package(default_visibility = ["//visibility:public"])

load("@my_deps//:requirements.bzl", "requirement")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@rules_proto//proto:defs.bzl", "proto_library")

# pazel-ignore
load("//:custom_rules.bzl", "custom_rule")

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
    deps = ["//foo:bar1"],
)

py_library(
    name = "bar1",
    srcs = ["bar1.py"],
    deps = [requirement("numpy")],
)

py_library(
    name = "bar2",
    srcs = ["bar2.py"],
    deps = [
        "//foo:bar1",
        requirement("pyyaml"),
    ],
)

py_binary(
    name = "bar3",
    srcs = ["bar3.py"],
)

py_library(
    name = "bar6",
    srcs = ["bar6.py"],
    deps = ["//xyz:abc1"],
)

proto_library(
    name = "baz_proto",
    srcs = ["baz.proto"],
    deps = [
        "//com/abc/protobuf:share_proto",
        "//foo:zap_proto",
    ],
)

py_proto_library(
    name = "baz_py_pb2",
    deps = [":baz_proto"],
)

py_library(
    name = "baz",
    srcs = ["baz.py"],
    deps = [requirement("foo")],
)

py_library(
    name = "foo",
    srcs = ["foo.py"],
)

# pazel-ignore
py_test(    # pazel would mark bar4.py as a library but it remains as a test because it is ignored.
    name = "bar4",
    srcs = ["bar4.py"],
    deps = [],
)

# pazel-ignore
custom_rule("bar5",  # pazel recognizes positional arguments, too.
            "bar5.py"
)

# My footer
