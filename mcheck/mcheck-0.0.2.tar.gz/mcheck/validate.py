#!/usr/bin/env python
# -*- coding: utf-8 -*-

from compute import Signature

class Validation():

    def handle(self, filename, method, target):
        sig = Signature()
        result, m = sig.produce(filename, method)
        return result == target, m


