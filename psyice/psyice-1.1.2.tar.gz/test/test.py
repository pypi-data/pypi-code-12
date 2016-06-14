#!/usr/bin/env python

import psyice
import os


def modifyMirrorlist(mirrorlist):
    """Modify Arch Linux mirrorlist, leaving only Chinese repos
        In order to use it, you should provide a parameter
        (the location of mirrorlist file)"""
    try:
        with open(mirrorlist) as dataRead:
            urls = []
            findChina = False
            urls = [eachLine for eachLine in dataRead]
            for eachLine in dataRead:
                if (not findChina and eachLine.find("China") != -1):
                    findChina = True
                if (findChina):
                    if (len(eachLine) != 1):
                        urls.append(eachLine[1:])
                    else:
                        break
        urls.pop(0)
        with open(mirrorlist, "w") as dataWrite:
            for each in urls:
                dataWrite.write(each)
            dataWrite.close()
            return None
    except IOError as ioerr:
        print("Error: " + str(ioerr))
