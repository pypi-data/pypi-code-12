# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.__init__.py : 
"""

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"
__version__ = "1.1.14"


'''Enable verbose output for the check points' execution'''
DEBUG = False


def default_colored(text, *args, **kwargs):
    """a default colored function used for print raw text without any color.
    """
    return text

try:
    from termcolor import colored
except:
    colored = default_colored

