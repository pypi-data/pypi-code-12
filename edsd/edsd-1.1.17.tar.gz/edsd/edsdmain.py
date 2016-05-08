#!/usr/local/python
# coding:utf-8
# Copyright (C) Alibaba Group

"""
EDAS detector - A simple script to detect the EDAS running environment.

$ edsd help
  show this document.

$ edsd list [check_id][.point_id]

$ edsd list 1

$ edsd list 1.1

$ edsd check 1

$ edsd check 1.1

$ edsd check all

$ edsd view [check_id.point_id]
"""

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"
from edsd import __version__, colored

try:
    import warnings
    warnings.filterwarnings("ignore")

    import getpass
    user = getpass.getuser()
    if user != 'admin':
        print colored("Warning", 'red') + \
              ": edsd is recommended running with user 'admin'"
        import sys
        sys.exit(1)

    import sys
    ver = sys.version_info
    if ver < (2, 6):
        print colored("Warning", 'red') + ': python version needs 2.6+'
except:
    pass


def collect():
    import edsd.collect
    edsd.collect.collect()


def main_shell():
    import edsd.cps
    import edsd.commandline
    cpc = edsd.commandline.CheckPointCmd()
    try:
        edsd.cps.install()
        cpc.cmdloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as _:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    collect()

