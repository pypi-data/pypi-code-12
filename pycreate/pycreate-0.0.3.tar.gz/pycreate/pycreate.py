#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is the main file containing all the logic for pycreate.
"""
import sys

def main(args):
    """
    Main function for pycreate

    :param args: command line parameters as list of strings
    """
    print("Hello World")

def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()
