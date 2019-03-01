from distutils.core import setup
import sys
import py2exe

sys.argv.append('py2exe')

packages = ["Crypto", "encodings"]

includes = ["pyodbc", "os", "datetime", "threading", "sys", "time", "ctypes", "base64",
            "inspect", "decimal", "servicemanager", "win32serviceutil", "win32service", "win32event",
            "asyncore", "functions", "gl", "sqlconns", "http.server", "maproxy"
            ]

# capitals are important in the service name
# the service is actually the name of the .py file you are building
setup(
    service=["iface_https_handler"],
    description="iface https handler for North Time Pro",
    modules=["iface_https_handler.py"],
    cmdline_style='pywin32',
    options={
        'py2exe': {
            "packages": packages,
            "includes": includes}
    }
)
