from __future__ import print_function, division, absolute_import

import os
import subprocess

import distributed
from distributed.cli.utils import check_python_3



dirname = os.path.dirname(distributed.__file__)
path = os.path.join(dirname, 'diagnostics', 'bokeh')

@click.command()
def main():
    proc = subprocess.Popen(['bokeh', 'serve', path])
    proc.join()


def go():
    check_python_3()
    main()

if __name__ == '__main__':
    go()
