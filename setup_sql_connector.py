from distutils.core import setup

import py2exe
import sys
import os

sys.argv.append('py2exe')

packages = ["Crypto"]

includes = ["pyodbc","os","datetime","sys","time","ctypes","base64",
            "inspect","decimal",
            "functions","gl","sqlconns","tkinter"
            ]

mydata_files = ["python_small.ico","python.png"]

#includes = ["pyodbc","os","datetime","threading","sys","time","ctypes","base64",
 #           "inspect","decimal","servicemanager","win32serviceutil","win32service","win32event",
  #          "asyncore","gl","sqlconns","functions",
   #         ]

#successfully built iob comm to exe with this...use when need to test
#setup(
#    name = "inbio Communicator",
#    description = "Inbio interface for North Time Pro",
#    windows = [{"script" : "inbio communicator.py"}],
#    options={
#        'py2exe' : {
#                    "packages":packages,
#                    "includes":includes}
#    }
#)

#capitals are important in the service name
#the service is actually the name of the .py file you are building
setup(
    options={
        'py2exe' : {"bundle_files": 2,
                    "compressed": True,
                    "packages":packages,
                    "includes":includes,
                    }
    },
    windows = [{
        'script': "sql connector.py",
        "icon_resources": [(1, "python_small.ico")]
    }],
    zipfile = None,
)
