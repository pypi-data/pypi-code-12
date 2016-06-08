# encoding: UTF-8

import sys, re, os

# python environment
IF_PYTHON_VERSION_2X = (lambda: re.match(r"^2.", sys.version))()
IF_PYTHON_VERSION_3X = (lambda: re.match(r"^3.", sys.version))()

# default setting for pexpect
TIMEOUT = 1
STDOUT = True
SPAWN = (lambda: os.environ['SHELL'])()
TERMINATION = 'exit'
