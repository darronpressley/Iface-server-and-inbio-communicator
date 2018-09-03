
from distutils.core import setup

import py2exe
import sys
import os


sys.argv.append('py2exe')

packages = ["Crypto","win32com","ctypes"]

excludes = ["Tkinter"]

#packages = ["Crypto","pyodbc","os","datetime","threading","sys","time","ctypes","base64","inspect","decimal"]
includes = ["os","sys","decimal","win32com","pythoncom","inspect","pyodbc","base64","datetime","time"]

#mydata_files = ["python_small.ico","python.png"]
mydata_files = [
      ]


#capitals are important in the service name
#the service is actually the name of the .py file you are building
setup(
    data_files=mydata_files,
    options={
        'py2exe' : {"optimize": 0,
                    "bundle_files": 3,
                    "packages":packages,
                    "includes":includes,
                    "excludes":excludes,
                    }
    },
    windows = [{
        'script': "inbio config.py",
        "icon_resources": [(1, "python_small.ico")]
    }]
)



