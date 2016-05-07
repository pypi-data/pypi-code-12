import sys

from expvar import ExpVar


class CmdlineExpVar(ExpVar):
    name = "cmdline"

    def value(self):
        return [sys.executable] + sys.argv
