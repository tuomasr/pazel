package(default_visibility = ["//visibility:public"])

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
    deps = [],
)

py_binary(
    name = "app",
    srcs = ["app.py"],
    deps = [
        ":generate_rule",
        ":helpers",
        ":output_build",
        ":parse_build",
        ":pazel_extensions",
    ],
)

py_library(
    name = "bazel_rules",
    srcs = ["bazel_rules.py"],
    deps = [],
)

py_library(
    name = "generate_rule",
    srcs = ["generate_rule.py"],
    deps = [
        ":bazel_rules",
        ":parse_build",
        ":parse_imports",
    ],
)

py_library(
    name = "helpers",
    srcs = ["helpers.py"],
    deps = [],
)

py_library(
    name = "output_build",
    srcs = ["output_build.py"],
    deps = [],
)

py_library(
    name = "parse_build",
    srcs = ["parse_build.py"],
    deps = [":helpers"],
)

py_library(
    name = "parse_imports",
    srcs = ["parse_imports.py"],
    deps = [":helpers"],
)

py_library(
    name = "pazel_extensions",
    srcs = ["pazel_extensions.py"],
    deps = [
        ":bazel_rules",
        ":generate_rule",
    ],
)
