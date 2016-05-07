import subprocess

from .startstop import start,stop


def get_pid(name):
    return subprocess.check_output(["pidof",name])


def build_change(**args):
    stop()
    start(args.build)
    pass
