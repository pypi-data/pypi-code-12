#!/usr/bin/env python
# -*- coding: utf-8 -*-

import algorithm

class Signature():

    def handle(self, filename, method):
        value,m = self.produce(filename, method)
        return value + " " + m

    def produce(self, filename, method):
        f = open(filename)
        data = f.read()
        f.close()
        m = method
        if method == None:
            m = "md5"
        return algorithm.strategy[m](data), m


