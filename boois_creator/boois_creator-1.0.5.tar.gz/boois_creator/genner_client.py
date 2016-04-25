#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import info_gener
if len(sys.argv)>1:

    json_file=sys.argv[1]
    case="python"
    out_path=sys.argv[2]+"/"
    info_gener.gen2(json_file,case,out_path)

