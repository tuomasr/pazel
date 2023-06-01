package(default_visibility = ["//visibility:public"])

py_library(
    name = "proto_deps",
    srcs = ["proto_deps.py"],
    deps = ["//pazel:helpers"],
)

py_test(
    name = "proto_deps_test",
    srcs = ["proto_deps_test.py"],
    size = "small",
    deps = [":proto_deps"],
)

py_library(
    name = "proto_rules",
    srcs = ["proto_rules.py"],
    deps = [
        "//pazel:bazel_rules",
    ],
)

py_test(
    name = "proto_rules_test",
    srcs = ["proto_rules_test.py"],
    size = "small",
    deps = [
        ":proto_rules",
        "//pazel:generate_rule",
    ],
)
