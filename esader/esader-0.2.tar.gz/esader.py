#!/usr/bin/env python
#-*-coding:utf-8-*-
from os import system

class esLor():
    bold = "\033[1m"
    underline = "\033[4m"
    green = "\033[92m"
    blue = "\033[94m"
    yellow = "\033[93m"
    red = "\033[91m"
    endcolor = "\033[0m"

def esLogo(ecoder, esoft, einfo, clean=None):
    if clean == None or clean == "notClear":
        print "--==[ "+esLor.bold+esLor.yellow+ecoder+esLor.endcolor
        print "--==[ "+esLor.bold+esLor.blue+esoft+esLor.endcolor
        print "--==[ "+esLor.bold+esLor.green+einfo+esLor.endcolor
    elif clean == "clear":
        system("clear")
        print "--==[ "+esLor.bold+esLor.yellow+ecoder+esLor.endcolor
        print "--==[ "+esLor.bold+esLor.blue+esoft+esLor.endcolor
        print "--==[ "+esLor.bold+esLor.green+einfo+esLor.endcolor
    else:
        pass
