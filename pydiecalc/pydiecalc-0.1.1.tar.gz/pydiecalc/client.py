import cmd
import os
import sys

from pydiecalc import CaughtRollParsingError
from pydiecalc import roll


def _perform_roll(line, variables):
    try:
        result, rolls = roll(line, variables)
        print(result)
    except CaughtRollParsingError:
        print("Bad roll format")


class PyDieCalc(cmd.Cmd):

    prompt = 'pydiecalc: '
    variables = {}

    def do_roll(self, line):
        _perform_roll(line, self.variables)

    def default(self, line):
        self.do_roll(line)

    def do_EOF(self, line):
        return True

    def do_exit(self, line):
        return True


def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        script = os.path.basename(sys.argv[0])
        print("Usage:")
        print("    %s <equation with dice notation>" % script)
        print("    %s  # for CLI" % script)
        exit(0)
    if len(sys.argv) > 1:
        line = " ".join(sys.argv[1:])
        _perform_roll(line, {})
        return
    PyDieCalc().cmdloop()

if __name__ == '__main__':
    main()
