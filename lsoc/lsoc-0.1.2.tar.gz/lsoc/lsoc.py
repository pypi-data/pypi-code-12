#!/usr/bin/python
import os
import sys


def lsoccmd():
    if not len(sys.argv) >1:
        lsoc = 'stat -c "%a %n" *'
        os.system(lsoc)
    else:
        myFile = str(sys.argv[1])
        lsoc = 'stat -c "%a %n" {0}'.format(myFile)
        os.system(lsoc)
