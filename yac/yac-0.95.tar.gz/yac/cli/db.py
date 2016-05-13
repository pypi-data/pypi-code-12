import argparse,sys,os
from sets import Set
import yac.cli.restoredb
import yac.cli.setupdb

from yac.cli.primer import show_primer

def main():

    # first argument is help, show primer
    if (len(sys.argv)==1 or sys.argv[1] == '-h'):

        show_primer(['db','primer'])

    else:

        # strip command from args list
        command = sys.argv[1]
        sys.argv = sys.argv[1:]

        if command == 'restore':

            return yac.cli.restoredb.main()

        else:

            print "yac db command not supported or known"
            show_primer(['db','primer'])