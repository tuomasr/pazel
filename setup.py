"""Entrypoint for starting with pazel.

Run:

`python setup.py install` to install pazel.
`python setup.py develop` to develop pazel.
`python setup.py test` to run pazel tests.
"""

from setuptools import setup, find_packages

DESCRIPTION = "Generate Bazel BUILD files for a Python project."

setup(
    name='pazel',
    version='0.3.2',
    description=DESCRIPTION,
    packages=find_packages(exclude=('sample_app', 'sample_app.foo', 'sample_app.tests')),
    entry_points={
        'console_scripts': ['pazel = pazel.app:main']
    },
    test_suite='pazel.tests'
)
