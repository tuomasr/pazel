def custom_rule(filename, src):
    native.py_library(
        name = filename,
        srcs = [src]
    )
