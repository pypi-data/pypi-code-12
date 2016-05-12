# -*- coding: utf-8 -*-
import sys
from . import context


if __name__ == '__main__':
    # python -m vebootstrap.init
    c = context.Context(sys.executable, "sample.py")
    c.setup()
