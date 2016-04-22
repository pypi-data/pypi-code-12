import argparse,sys,os
import yac.cli.stack
import yac.cli.service
import yac.cli.db
import yac.cli.prefs
import yac.cli.container
import yac.cli.ssh

from yac.cli.primer import show_primer

def main():

    # first argument is help
    if (len(sys.argv)==1 or sys.argv[1] == '-h'):

        show_primer(['primer'])

    # last argument is primer
    elif sys.argv[len(sys.argv)-1] == 'primer':

        # show primer instructions
        show_primer(sys.argv[1:])

    else:

        # strip command from args list
        command = sys.argv[1]
        sys.argv = sys.argv[1:]

        if command == 'stack':

            return yac.cli.stack.main()

        elif command == 'service':

            return yac.cli.service.main()

        elif command == 'prefs':

            return yac.cli.prefs.main()    

        elif command == 'container':

            return yac.cli.container.main()    

        elif command == 'ssh':

            return yac.cli.ssh.main()
        else:

            return "command not supported, or not yet implemented"
        