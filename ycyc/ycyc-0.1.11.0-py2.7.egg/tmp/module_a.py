#!/usr/bin/env python
# encoding: utf-8

import module_b
from ycyc.base.lazyutils import LazyEnv
GlobalEnv = LazyEnv()
GlobalEnv.val = "a"
GlobalEnv.txt = lambda: "i'm not " + module_b.GlobalEnv.val
