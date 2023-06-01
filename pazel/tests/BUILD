package(default_visibility = ["//visibility:public"])

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
    deps = [],
)

py_test(
    name = "test_generate_rule",
    srcs = ["test_generate_rule.py"],
    size = "small",
    deps = ["//pazel:generate_rule"],
)

py_test(
    name = "test_helpers",
    srcs = ["test_helpers.py"],
    size = "small",
    deps = ["//pazel:helpers"],
)

py_test(
    name = "test_pazel_extensions",
    srcs = ["test_pazel_extensions.py"],
    size = "small",
    deps = ["//pazel:pazel_extensions"],
)
