from __future__ import print_function

import subprocess
import sys
import time


def execute(
        command,
        count=0,
        quit_on_zero=False,
        beep_on_zero=False,
        quit_on_nonzero=False,
        beep_on_nonzero=False,
        always_exit_zero=False,
        print_exit_code=False,
        silent=False,
        interval=1,
):
    stdout = sys.stdout
    stderr = sys.stderr

    if silent:
        stdout = subprocess.DEVNULL
        stderr = subprocess.DEVNULL

    i = 0
    while count <= 0 or i < count:
        exit_code = subprocess.call(command, stdout=stdout, stderr=stderr, stdin=sys.stdin)

        if print_exit_code:
            print("Exit code: {}".format(exit_code), file=sys.stderr)

        if exit_code == 0:
            if beep_on_zero:
                beep()
            if quit_on_zero:
                return exit_code
        else:
            if beep_on_nonzero:
                beep()
            if quit_on_nonzero:
                if always_exit_zero:
                    exit_code = 0
                return exit_code
        time.sleep(interval)
        count += 1


def beep():
    print('\a')
    # sys.stdout.write("\033[F")
