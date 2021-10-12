from __future__ import print_function

import time
from .bar2 import increment_sample
from . import sample


def main():
    print("Hello pazel.")
    sample()
    increment_sample()


main()