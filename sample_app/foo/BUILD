package(default_visibility = ["//visibility:public"])

load("@my_deps//:requirements.bzl", "requirement")

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
