from distutils.core import setup

import py2exe
import sys
import os

sys.argv.append('py2exe')

packages = ["Crypto"]
  
includes = ["pyodbc","os","datetime","threading","sys","time","ctypes","base64",
            "inspect","decimal","servicemanager","win32serviceutil","win32service","win32event",
            "asyncore","functions","gl","sqlconns","http.server"
            ]

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
#setup(
#    service = ["ifaceserver"],
#    description = "iface server for North Time Pro",
#    options={
#        'py2exe' : {
#                    "packages":packages,
#                    "includes":includes,
#                    "bundle_files": 1,
#                    "compressed": True
#                    }
#            },
#    zipfile = None,
#)
setup(
    service = ["ifaceserver"],
    description = "iface server for North Time Pro",
    options={
        'py2exe' : {
                    "packages":packages,
                    "includes":includes}
    }
)
