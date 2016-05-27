import argparse,sys,os
import yac.cli.build
import yac.cli.push
import yac.cli.start
#import yac.cli.stop

from yac.cli.primer import show_primer

def main():

    # first argument is help, show primer
    if (len(sys.argv)==1 or sys.argv[1] == '-h'):

        show_primer(['container','primer'])

    else:

        # strip command from args list
        command = sys.argv[1]
        sys.argv = sys.argv[1:]

        if command == 'start':

            return yac.cli.start.main()
        
        #elif command == 'stop':

        #    return yac.cli.stop.main()

        elif command == 'build':

            return yac.cli.build.main()

        elif command == 'push':

            return yac.cli.push.main()

        else:

            print "Command not supported or known"
            show_primer(['container','primer'])