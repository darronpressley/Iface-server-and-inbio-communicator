from distutils.core import setup

import py2exe, sys, os

sys.argv.append('py2exe')

packages = ["Crypto","pyodbc","os","datetime","threading","sys","time",
            "ctypes","base64","inspect","decimal",
            "servicemanager","win32serviceutil","win32service","win32event",
            "asyncore"
            ]

#setup(
#    service = ["Inbio Communicator"],
#    description = "Inbio interface for North Time Pro",
#    modules = ["inbio communicator.py"],
#    cmdline_style='pywin32',
#    version = '0.0.1',
#    name='Inbio Communicator',
#    options={
#        'py2exe': {
#            'includes': packages}}
#   )


setup(
    service = ["Inbio Communicator"],
    description = "Inbio interface for North Time Pro",
    modules = ["inbio communicator.py"],
    cmdline_style='pywin32',
    options={
        'py2exe':{'includes': packages}
            }
)