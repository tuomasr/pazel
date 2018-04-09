package(default_visibility = ["//visibility:public"])
load("@my_deps//:requirements.bzl", "requirement")

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
    deps = [],
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
    deps = [],
)

