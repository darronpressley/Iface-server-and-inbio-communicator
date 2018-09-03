import sys
from cx_Freeze import setup, Executable

base = "Win32GUI"

includes = []
includefiles = ["python_small.ico","python.png"]
excludes = []
packages = ["Crypto","pyodbc","os","datetime","threading","sys","time","ctypes","base64","inspect","decimal"]
exe = Executable("adp.py", base=base, icon='python_time.ico')

#options = {"build_exe": {"packages":["wx","wx.grid","pyodbc","Crypto","inspect"], "include_files":["python_small.ico"]}},
setup(
    name = "adp",
    options = {"build_exe": {"includes":includes, "excludes":excludes,"packages":packages,"include_files":includefiles}},
    version = "0.01",
    description = "adp",
    executables = [exe]
    )

