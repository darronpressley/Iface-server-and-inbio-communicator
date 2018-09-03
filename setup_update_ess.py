
from distutils.core import setup

import py2exe
import sys
import os

includes = ["os","sys","decimal","fileinput"]

sys.argv.append('py2exe')

setup(
    zipfile=None,
    options={"py2exe": {"bundle_files": 1}},
    console=[r'essconfig.py'])




