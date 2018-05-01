package(default_visibility = ["//visibility:public"])

load("@my_deps//:requirements.bzl", "requirement")
load("//:custom_rules.bzl", "py_doctest")

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
)

py_test(
    name = "test_bar1",
    srcs = ["test_bar1.py"],
    size = "medium",
    data = ["test_data/dummy"],
    deps = [
        "//foo:bar1",
        requirement("requests"),
    ],
)

py_test(
    name = "test_bar2",
    srcs = ["test_bar2.py"],
    size = "large",
    deps = ["//foo:bar2"],
)

py_test(
    name = "test_bar3",
    srcs = ["test_bar3.py"],
    size = "small",
    data = glob(["test_data/*.png"]),
)

py_doctest(
    "test_doctest",
    "test_doctest.py",
    deps = [],
)

# My footer
