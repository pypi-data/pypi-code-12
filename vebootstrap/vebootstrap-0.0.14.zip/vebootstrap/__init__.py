# -*- coding: utf-8 -*-
import sys


if sys.argv and sys.argv[0] in ('-c', '-m'):
    # sys.argv[0] is different on runtime version when a "-m" option is specified
    # >>> python -m vebootstrap hogehoge.py
    #   python2: sys.argv[0] == '-c'
    #   python3: sys.argv[0] == '-m'
    pass
else:
    # vebootstrap imported from [pyfile]
    from . import context
    c = context.Context(sys.executable, sys.argv[0])
    c.bootstrap(sys.argv[1:])

