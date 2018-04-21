from setuptools import setup, find_packages

description = "Generate Bazel BUILD files for a Python project."

setup(
    name='pazel',
    version='0.1.0',
    description=description,
    packages=find_packages(exclude=('sample_app', 'sample_app.foo', 'sample_app.tests')),
    entry_points = {
        'console_scripts': ['pazel = pazel.app:main']
    },
    test_suite='pazel.tests'
)