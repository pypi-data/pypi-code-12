#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import algorithm

class SignatureFile():

    def handle(self, directory, method):
        m = method
        if method == None:
            m = "md5"
        savefilename = os.path.dirname(os.path.abspath(directory)) + "." + m
        savefile = open(savefilename, 'w')
        content = ""
        for dirpath,dirnames,filenames in os.walk(directory):
            for filename in filenames:
                file = open(dirpath + "/" + filename)
                data = file.read()
                content += algorithm.strategy[m](data) + " " + dirpath + "/" + filename + "\n"
                file.close()
        savefile.write(content)
        savefile.close()
        return savefilename

