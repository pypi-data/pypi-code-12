#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import subprocess


VERSION = "0.2.0"
README_DIR = ".."
README_WORK_DIR = "."
README_HEADER_PATH = os.path.join(README_WORK_DIR, "README_HEADER.rst")


with open(os.path.join(README_WORK_DIR, "summary.txt")) as f:
    summary = [line.strip() for line in f if line.strip()]


def main():
    convert_command = "pandoc -f markdown -t rst README.md"
    process = subprocess.Popen(
        convert_command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret_stdout, _ret_stderr = process.communicate()

    with open(os.path.join(README_DIR, "README.rst"), "w") as f:
        f.write("\n".join([
            line.rstrip() for line in open(README_HEADER_PATH).readlines()
        ]))
        f.write("\n" * 2)
        f.write("Summary\n")
        f.write("=======\n")
        f.write("\n".join([line.rstrip() for line in summary]))
        f.write("\n" * 2)
        f.write("\n".join([line.rstrip() for line in ret_stdout.splitlines()]))
        f.write("\n")

if __name__ == '__main__':
    sys.exit(main())
