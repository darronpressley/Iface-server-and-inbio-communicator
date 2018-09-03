import sys
from cx_Freeze import setup, Executable

packages = ['win32serviceutil','win32service','win32event','servicemanager','socket','win32timezone','ServiceHandler']
build_exe_options = {"packages": packages}
executable = Executable("inbio communicator.py", base = "Win32Service",
        targetName = "Inbio communicator.exe",
        icon='python_time.ico')

setup(
        name = "Inbio Communicator",
        version = "0.0.1",
        description = "Inbio Communicator from North Time and Data",
        executables = [executable],
        options = dict(build_exe = build_exe_options))