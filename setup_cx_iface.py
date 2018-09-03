from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'includes': ['tornado']
    }
}

import sys
sys.argv.append('build')

executables = [
    Executable('config.py', base='console',
               targetName='ifaceserver.exe')
]

setup(name='Ifaceserver',
      version='2018.0.5000',
      description='Ifaceserver',
      executables=executables,
      options=options
      )

