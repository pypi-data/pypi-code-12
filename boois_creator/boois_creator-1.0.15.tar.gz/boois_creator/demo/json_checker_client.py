#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from utils.obj_json_checker import ObjJsonChecker

if len(sys.argv)>1:
    filename=sys.argv[1].replace("\\","/")
    obj_name=filename.split("/")[-1].split(".")[0]
    # print obj_name
    # exit()
    with open(filename,"r") as f:
        txt=f.read()
    ret=ObjJsonChecker().check(obj_name, txt)
    print "check result: %s" % "success" if ret else "fail"