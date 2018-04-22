def custom_rule(filename, src):
    native.py_library(
        name = filename,
        srcs = [src]
    )

def py_doctest(filename, src, deps=None, data=None):
    if deps == None:
        deps = []

    if data == None:
        data = []

    native.py_binary(
        name = filename,
        srcs = [src],
        deps = deps,
        data = data,
        args = ['-v']
    )