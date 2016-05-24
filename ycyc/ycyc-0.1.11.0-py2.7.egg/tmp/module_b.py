#!/usr/bin/env python
# encoding: utf-8

import module_a
from ycyc.base.lazyutils import LazyEnv
GlobalEnv = LazyEnv()
GlobalEnv.val = "b"
GlobalEnv.txt = lambda: "i'm not " + module_a.GlobalEnv.val
