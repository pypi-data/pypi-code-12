#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-28 13:31:51
# Filename      : command.py
# Description   : 

from __future__ import print_function, unicode_literals
import optparse

def parse():
    parser = optparse.OptionParser()
    parser.add_option('-l', '--list', dest = 'list_nodes', 
            help = 'list all proxy nodes', action = 'store_true')

    options, args = parser.parse_args()
    options.args = args

    return options

