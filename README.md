# pazel - generate Bazel BUILD files for Python

## Requirements

### pazel
No requirements. Tested on Python 2.7 and 3.6 on Ubuntu 16.04 and macOS High Sierra.

### Bazel
Tested on Bazel 0.11.1. All recent versions are expected to work.

## Installation

```
> git clone https://github.com/gobeil/pazel.git
> cd pazel
> python setup.py install
```

## Usage

NOTE: `pazel` overwrites any existing BUILD files. Please use version control or have backups of
your current BUILD files before using `pazel`.

### Default usage with Bazel

The following example generates all BUILD files for the sample Python project in `sample_app`.
Start from the `pazel` root directory to which the repository was cloned.

```
> bazel run //pazel:app -- <pazel_root_dir>/sample_app -r <pazel_root_dir>/sample_app
-c <pazel_root_dir>/sample_app/.pazelrc
Generated BUILD files for <pazel_root_dir>/sample_app.
```

### Default usage without Bazel

Start from the `pazel` root directory.

```
> cd sample_app
> pazel
Generated BUILD files for <pazel_install_dir>/sample_app.
```

### Bazel Rules Generated

- [Python Conventions](pazel/languages/py/conventions.md)
- [Protocol Buffer Conventions](pazel/languages/proto/conventions.md)

### Testing the generated BUILD files

Now, we can build, test, and run the sample project by running the following invocations in the
`sample_app` directory, respectively.

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

`pazel` config file `.pazelrc` is read from the current working directory. Use
`pazel -c <pazelrc_path>` to specify an alternative path.

### Ignoring rules in existing BUILD files

The tag `# pazel-ignore` causes `pazel` to ignore the rule that immediately follows the tag in an
existing BUILD file. In particular, the tag can be used to skip custom rules that `pazel` does not 
handle. `pazel` places the ignored rules at the bottom of the BUILD file. See `sample_app/foo/BUILD`
for an example using the tag.


### Customizing and extending pazel

`pazel` can be programmed using a `.pazelrc` Python file, which is read from the current
working directory or provided explicitly with `pazel -c <pazelrc_path>`.

The user can define variables `HEADER` and `FOOTER` to add custom header and footer to
all BUILD files, respectively. See `sample_app/.pazelrc` and `sample_app/BUILD` for an example that
adds the same `visibility` to all BUILD files.

If some pip package has different install name than import name, then the user
should define `EXTRA_IMPORT_NAME_TO_PIP_NAME` dictionary accordingly. `sample_app/.pazelrc` has
`{'yaml': 'pyyaml'}` as an example. In addition, the user can specify local packages and their
corresponding Bazel dependencies using the `EXTRA_LOCAL_IMPORT_NAME_TO_DEP` dictionary.

The user can add support for custom Bazel rules by defining a new class implementing the `BazelRule`
interface in `pazel/bazel_rules.py` and by adding that class to `EXTRA_BAZEL_RULES` list in
`.pazelrc`. `sample_app/.pazelrc` defines a custom `PyDoctestRule` class that identifies all
doctests and generates custom `py_doctest` Bazel rules for them as defined in
`sample_app/custom_rules.bzl`.

In addition, the user can implement custom rules for mapping Python imports to Bazel dependencies
that are not natively supported. That is achieved by defining a new class implementing the
`InferenceImportRule` interface in `pazel/import_inference_rules.py` and by adding the class to
`EXTRA_IMPORT_INFERENCE_RULES` list in `.pazelrc`. `sample_app/.pazelrc` defines a custom
`LocalImportAllInferenceRule` class that generates the correct Bazel dependencies for
`from X import *` type of imports where `X` is a local package.


## BUILD file formatting

`pazel` generates BUILD files that are nearly compatible with
[Buildifier](https://github.com/bazelbuild/buildtools/tree/master/buildifier). Buildifier can be
applied on `pazel`-generated BUILD files to remove the remaining differences, if needed.