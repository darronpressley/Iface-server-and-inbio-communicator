import cx_Freeze
import sys

bas = None

if sys.platform== "win32":
    base = "Win32GUI"

executables = [cx_Freeze.Executable("Inbio Communicator.py", base=base, icon='python_time.ico')]

cx_Freeze.setup(
    name = "Inbio Communicator",
    option = {"build_exe": {"packages":[], "include_files":["python_small.ico"]}},
    version = "0.01",
    description = "Inbio Communicator",
    executables = executables
    )

