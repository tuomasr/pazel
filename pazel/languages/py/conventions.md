# Python Conventions

## Bazel Rule Generation

There are three commonly used [Python rules](https://bazel.build/reference/be/python):

- `py_binary` - An executable Python program
- `py_test` - A Python test
- `py_library` - Any python code that isn't a program or a test

If a `.py` file has an entry point in it:
```
if __name__ == "__main__":
```
Then a `py_binary` will be generated.

If a `.py` file's name starts or ends with `_test`, imports the `unittest` namespace, or uses `unittest.TestCase`, a `py_test` will be generated:

Any other `.py` file will produce a `py_library`.

## Dependency Extraction

TODO

### Protocol Buffers

Dependencies on a protocol buffer are identified by a `_pb2` or `_pb2_grpc` postfix on the imported symbol, and will target the matching `py_proto_library` by [protocol buffer conventions](../proto/conventions.md) to have name ending in `_py_pb2` or `_py_pb2_grpc` respectively, for example:

```
import todolist_pb2 as TodoList
```

Will add the following to the `py_library` rule deps list:

```
py_library(
    deps = [
        ":todolist_py_pb2",
        ...
    ]
)
```

Unless it is otherwise mapped by the `.pazelrc` file.
