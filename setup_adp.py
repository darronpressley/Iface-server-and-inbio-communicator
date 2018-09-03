
from distutils.core import setup

import py2exe
import sys
import os


sys.argv.append('py2exe')

packages = ["Crypto","win32com"]

excludes = ["Tkinter"]

#includes = ["os","sys","decimal","win32com.client","PyQt4","sip"
           # ]
includes = ["os","sys","decimal","PyQt4","sip","win32com","pythoncom"
            ]
#mydata_files = ["python_small.ico","python.png"]
mydata_files = [
      ('imageformats', [
        r'C:\Python34\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll'
        ])
      ]
    #('pywin32_system32',[
     #     r'C:\Python34\Lib\site-packages\pywin32_system32\pythoncom34.dll',
      #      r'C:\Python34\Lib\site-packages\pywin32_system32\pywintypes34.dll'
      #])
       # ]

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
    data_files=mydata_files,
    options={
        'py2exe' : {"bundle_files": 1,
                    "packages":packages,
                    "includes":includes,
                    "excludes":excludes,
                    }
    },
    windows = [{
        'script': "adp.py",
        "icon_resources": [(1, "python_small.ico")]
    }],
    zipfile=None
)
