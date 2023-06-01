package(default_visibility = ["//visibility:public"])

py_library(
    name = "py_deps",
    srcs = ["py_deps.py"],
    deps = ["//pazel:helpers"],
)

py_test(
    name = "py_deps_test",
    srcs = ["py_deps_test.py"],
    size = "small",
    deps = [":py_deps"],
)

py_library(
    name = "py_rules",
    srcs = ["py_rules.py"],
    deps = [
        "//pazel:bazel_rules",
    ],
)

py_test(
    name = "py_rules_test",
    srcs = ["py_rules_test.py"],
    size = "small",
    deps = [
        ":py_rules",
        "//pazel:generate_rule",
    ],
)
