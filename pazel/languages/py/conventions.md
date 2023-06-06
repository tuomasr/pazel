# Python Conventions

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
