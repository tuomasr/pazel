# pazel - generate Bazel BUILD files for Python

## Requirements

### pazel
No requirements. Tested on Python 2.7 and 3.6 on Ubuntu 16.04 and macOS High Sierra.

### Bazel
Tested on Bazel 0.11.1. All recent versions are expected to work.

## Installation

```
> git clone https://github.com/tuomasr/pazel.git
> cd pazel
> python setup.py install
```

## Usage

### Default usage

The following example generates all BUILD files for the sample Python project in `sample_app`.

```
> cd sample_app   # Assumes that you are in the pazel root directory containing setup.py.
> pazel
Generated BUILD files for <pazel_install_dir>/sample_app.
```

Now, we can build, test, and run the sample project using the invocations below, respectively.

```
> bazel build
> bazel test ...
> bazel run foo:bar3
```

### Command-line options

`pazel -h` shows a summary of the command-line options. Each of them is explained below.

By default, BUILD files are generated recursively for the current working directory.
Use `pazel <some_path>` to generate BUILD file(s) recursively for another directory
or for a single Python file.

All imports are assumed to be relative to the current working directory. For example,
`sample_app/foo/bar2.py` imports from `sample_app/foo/bar1.py` using `from foo.bar1 import sample`.
Use `pazel -r <some_path>` to override the path to which the imports are relative.

By default, `pazel` adds rules to install all external Python packages. If your environment has
pre-installed packages for which these rules are not required, then use `pazel -p`.


### Working with custom Bazel rules and ignoring rules in existing BUILD files

The tag `# pazel-ignore` causes `pazel` to ignore the rule that immediately follows it in an
existing BUILD file. See `sample_app/foo/BUILD` for an example using the tag.
This feature can be applied to custom rules, in particular. `pazel` places the ignored rules
at the bottom of the BUILD file.
