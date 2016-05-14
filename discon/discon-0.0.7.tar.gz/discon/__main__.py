#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR%  <>
#
# Distributed under terms of the %LICENSE% license.

"""

"""

import logging

logger = logging.getLogger(__name__)
import argparse
import subprocess
import os.path as op

def make(args):
    if not op.exists("build.sh"):
        with open('build.sh', 'a') as the_file:
            the_file.write('#!/bin/bash\n\n$PYTHON setup.py install\n')
    if not op.exists("bld.bat"):
        with open('bld.bat', 'a') as the_file:
            the_file.write('"%PYTHON%" setup.py install\nif errorlevel 1 exit 1')

    if (args.bumptype == "patch"):
        print "pull, patch, push, push --tags"
        subprocess.call("git pull", shell=True)
        subprocess.call("bumpversion patch", shell=True)
        subprocess.call("git push", shell=True)
        subprocess.call("git push --tags", shell=True)
    elif (args.bumptype == "minor"):
        print "pull, patch, push, push --tags"
        subprocess.call("git pull", shell=True)
        subprocess.call("bumpversion minor", shell=True)
        subprocess.call("git push", shell=True)
        subprocess.call("git push --tags", shell=True)
    elif (args.bumptype == "major"):
        print "pull, patch, push, push --tags"
        subprocess.call("git pull", shell=True)
        subprocess.call("bumpversion major", shell=True)
        subprocess.call("git push", shell=True)
        subprocess.call("git push --tags", shell=True)
    elif (args.bumptype == "stable"):
        subprocess.call("git push --tags", shell=True)
        subprocess.call("git checkout stable", shell=True)
        subprocess.call("git pull origin master", shell=True)
        subprocess.call("git push", shell=True)
        subprocess.call("git checkout master", shell=True)
        return
# fi
    # upload to pypi


    logger.debug("pypi upload")
    subprocess.call(["python", "setup.py", "register", "sdist", "upload"])

    # build conda and upload
    logger.debug("conda clean")

    try:
        subprocess.call(["rm ", "-rf ", "win-*"])
    except OSError:
        pass
    try:
        subprocess.call(["rm ", "-rf ", "linux-*"])
    except OSError:
        pass
    try:
        subprocess.call(["rm ", "-rf ", "osx-*"])
    except OSError:
        pass

    logger.debug("conda build")

    # subprocess.call("conda build -c mjirik -c SimpleITK .", shell=True)
    subprocess.call("conda build .", shell=True)
    subprocess.call("conda convert -p all `conda build --output .`", shell=True)

    logger.debug("binstar upload")
    subprocess.call("binstar upload */*.tar.bz2", shell=True)

    logger.debug("rm files")
    try:
        subprocess.call(["rm ", "-rf ", "win-*"])
    except OSError:
        pass
    try:
        subprocess.call(["rm ", "-rf ", "linux-*"])
    except OSError:
        pass
    try:
        subprocess.call(["rm ", "-rf ", "osx-*"])
    except OSError:
        pass


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "bumptype",
        default=None)
    parser.add_argument(
        '-i', '--inputfile',
        default=None,
        # required=True,
        help='input file'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        ch.setLevel(logging.DEBUG)

    make(args)


if __name__ == "__main__":
    main()