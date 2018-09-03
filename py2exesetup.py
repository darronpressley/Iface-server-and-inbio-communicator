from distutils.core import setup
import py2exe


setup(
    service = ["test2"],
    description = "Inbio interface for North Time Pro",
    modules = ["test2.py"],
    cmdline_style='pywin32',
   )

