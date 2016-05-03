#!/usr/bin/env python
#coding:utf-8
"""
  Author:  Yeison Cardona --<yeison.eng@gmail.com>
  Purpose:
  Created: 13/02/16
"""

import os
import sys
import random
from subprocess import call

from .tools import read_data


MSE_BIN = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mse", "mse")



########################################################################
class MSE:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, dataset, data_dir=None):
        """Constructor"""
        self.data = read_data(dataset)

        if data_dir:
            self.DATA_DIR = data_dir
        else:
            self.DATA_DIR = "~/.tmp"
            self.DATA_DIR = os.path.expanduser(self.DATA_DIR)

        if not os.path.exists(self.DATA_DIR):
            os.mkdir(self.DATA_DIR)



    #----------------------------------------------------------------------
    def get(self, scale=20, a=1, m=2, M=2, b=1, r=0.15, R=0.15, i=0, I=None):
        """
        -c args seems be bugged


        """
        filename = self.__save_file__(self.data)

        if I is None:
            I = self.data.shape[0]

        if not filename:
            return False, False

        filename_out = filename.replace(".data", ".mse")
        command = "{MSE_BIN} -n {scale} <'{filename}'>'{filename_out}'".format(MSE_BIN=MSE_BIN, **locals())
        #command = "{MSE_BIN} -n {scale} -r {r} -a {a} -m {m} -M {M} -b {b} -R {R} -i {i} -I {I} <'{filename}'>'{filename_out}'".format(MSE_BIN=MSE_BIN, **locals())


        return_code = call(command, shell=True)

        file = open(filename_out, "r")
        lines = file.readlines()
        file.close()

        mse = list(map(lambda x:(int(x[:x.find("\t")].replace("\n", "").replace("\t", "")), abs(float(x[x.find("\t")+1:].replace("\n", "").replace("\t", "")))), lines[4:]))

        os.remove(filename)
        os.remove(filename_out)

        return {
            "r": r,
            "m": m,
            "mse": dict(mse),
        }




    #----------------------------------------------------------------------
    def __save_file__(self, data):
        """"""
        name = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for n in range(10)])
        filename = os.path.join(self.DATA_DIR, name+".data")

        file = open(filename, "w")
        if data.any():
            for d in data:
                file.write(str(d) + "\n")
            file.close()
            return filename
        else:
            return False


