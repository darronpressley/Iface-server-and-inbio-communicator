# =============================================================================
#     Author: K Perkins
#     Date:   Jul 25, 2013
#     Taken From: http://programmingnotes.freeweq.com/
#     File:  setup.py
#     Description: This is the cx_Freeze setup file for creating an exe program
# =============================================================================
import sys
from cx_Freeze import setup, Executable

import os

os.environ['TCL_LIBRARY'] = 'c:/python36/tcl/tcl8.6'
os.environ['TK_LIBRARY'] = 'c:/python36/tcl/tk8.6'

# NOTE: you can include any other necessary external imports here aswell
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Dependencies are automatically detected, but it might need fine tuning.
buildOptions = dict(
    packages = [],
    excludes = [],
    include_files=['c:/python36/DLLs/tcl86t.dll', 'c:/python36/DLLs/tk86t.dll']
)


includefiles = ["python_small.ico","python.PNG"] # include any files here that you wish

includes = []
excludes = []
packages = ["crypto"]
 
#exe = Executable(
# # what to build
#   script = "SQL connector.py", # the name of your main python script goes here
#   initScript = None,
#   base = "Win32GUI", # if creating a GUI instead of a console app, type "Win32GUI"
#   targetName = "SQLconnector.exe", # this is the name of the executable file
#   copyDependentFiles = True,
#   compress = True,
#   appendScriptToExe = True,
#   appendScriptToLibrary = True,
#   icon = "python_time.ico" # if you want to use an icon file, specify the file name here
#)
 
setup(
 # the actual setup & the definition of other misc. info
    name = "SQLConnector", # program name
    version = "0.1",
    description = 'SQL Connector',
    author = "Dazza",
    author_email = "darronpressley@gmail.com",
    options = {"build_exe": buildOptions},
    #options = {"build_exe": {"excludes":excludes,"packages":packages,
    #  "include_files":includefiles}},
    executables = [Executable("sql connector.py", base=base)])
