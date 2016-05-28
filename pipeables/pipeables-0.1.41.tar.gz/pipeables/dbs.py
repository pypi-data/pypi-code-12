import sys
import os
import json

home = os.path.expanduser("~")

pipeablesdir = home + "/.pipeables"


def getDBs():
    dbconf_path = ""
    if os.path.isfile(os.getcwd()+"/dbconf.json"):
        dbconf_path = os.getcwd()+"/dbconf.json"
    else:
        if not os.path.isfile(pipeablesdir + "/dbconf.json"):
            print "Can't find dbconf.json in the home direcotry :" + home

        if not os.path.isdir(pipeablesdir):
            print "Can't find pipeables dir :" + pipeablesdir
            sys.exit(1)

        if not os.path.isfile(pipeablesdir + "/dbconf.json"):
            print "Can't find dbconf.json here  :" + pipeablesdir + "/dbconf.json"
            sys.exit(1)

        dbconf_path = pipeablesdir + "/dbconf.json"

    f = open(dbconf_path)
    dbs = json.loads(f.read())

    return dbs


def getDBsFromFile(f):
    f = open(f, "r")
    dbs = json.loads(f.read())

    return dbs
