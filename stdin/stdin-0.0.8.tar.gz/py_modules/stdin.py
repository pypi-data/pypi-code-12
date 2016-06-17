#!/usr/bin/env python
import os
import sys

__all__ = ["STDIN"]

STDIN = None
if os.fstat(sys.stdin.fileno()).st_size > 0:
    STDIN = sys.stdin.read()
