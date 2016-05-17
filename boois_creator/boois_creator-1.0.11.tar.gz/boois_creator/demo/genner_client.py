#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import creator
if len(sys.argv)>1:

    json_file=sys.argv[1]
    case="python"
    out_path=sys.argv[2]+"/"
    creator.gen2(json_file, case, out_path)

