import sys
from cx_Freeze import setup, Executable

import os
sys.argv.append('build')
os.environ['TCL_LIBRARY'] = 'c:/python36/tcl/tcl8.6'
os.environ['TK_LIBRARY'] = 'c:/python36/tcl/tk8.6'

# NOTE: you can include any other necessary external imports here aswell
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Dependencies are automatically detected, but it might need fine tuning.
buildOptions = dict(
    packages=[],
    excludes=[],
    includes = ["atexit","PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets"],
    include_files=['c:/python35/DLLs/tcl86t.dll', 'c:/python36/DLLs/tk86t.dll']
)

includefiles = ["python_small.ico", "python.PNG"]  # include any files here that you wish


excludes = []
packages = ["crypto"]

# Dependencies are automatically detected, but it might need fine tuning.


setup(
    # the actual setup & the definition of other misc. info
    name="SQL Connector",  # program name
    version="0.1",
    description='SQl Connector',
    author="Dazza",
    author_email="darronpressley@gmail.com",
    options={"build_exe": buildOptions},
    # options = {"build_exe": {"excludes":excludes,"packages":packages,
    #  "include_files":includefiles}},
    executables=[Executable("sql connector.py", base=base, icon='python_time.ico')])
