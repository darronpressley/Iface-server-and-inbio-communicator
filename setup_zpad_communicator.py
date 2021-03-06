from distutils.core import setup
import sys
import py2exe

sys.argv.append('py2exe')

packages = ["Crypto"]

includes = ["pyodbc", "os", "datetime", "threading", "sys", "time", "ctypes", "base64",
            "inspect", "decimal", "servicemanager", "win32serviceutil", "win32service", "win32event",
            "asyncore", "functions", "gl", "sqlconns"
            ]

# includes = ["pyodbc","os","datetime","threading","sys","time","ctypes","base64",
#           "inspect","decimal","servicemanager","win32serviceutil","win32service","win32event",
#          "asyncore","gl","sqlconns","functions",
#         ]

# successfully built iob comm to exe with this...use when need to test
# setup(
#    name = "inbio Communicator",
#    description = "Inbio interface for North Time Pro",
#    windows = [{"script" : "inbio communicator.py"}],
#    options={
#        'py2exe' : {
#                    "packages":packages,
#                    "includes":includes}
#    }
# )

# capitals are important in the service name
# the service is actually the name of the .py file you are building
setup(
    service=["zpad communicator"],
    description="zpad communicator for North Time Pro",
    modules=["zpad communicator.py"],
    cmdline_style='pywin32',
    options={
        'py2exe': {"bundle_files": 3,
            "packages": packages,
            "includes": includes}
    },
    zipfile=None
)
