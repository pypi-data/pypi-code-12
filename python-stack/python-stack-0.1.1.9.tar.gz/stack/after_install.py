# coding:utf8

import sys
import os

if sys.version_info[:2] < (3, 5):
    os.system('pip install -r ./requirements2.txt')
    os.system('python stack/stack_init.py')
    os.system('python3 install setup.py')
#
