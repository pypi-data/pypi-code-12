'''
Created on May 18, 2016

@author: zhizhang
'''

import main
import sys

def main1():
    if len(sys.argv)>1:
        main.main(sys.argv[1])
    else:
        print 'USAGE: %s <CONFIGFILE.INI>'%'sum_rnaseq'
        sys.exit() 