#!C:\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'excel-export==0.1.1','console_scripts','excel-export'
__requires__ = 'excel-export==0.1.1'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('excel-export==0.1.1', 'console_scripts', 'excel-export')()
    )
