from .command import Command
from matador import zippey
import io
import sys


class FilterZip(Command):

    input = io.open(sys.stdin.fileno(), 'rb')
    output = io.open(sys.stdout.fileno(), 'wb')
    action = None

    actions = {
        'smudge': zippey.decode,
        'clean': zippey.encode
    }

    def _execute(self):
        zippey.init()
        if self.action is not None:
            self.actions[self.action](self.input, self.output)


class SmudgeZip(FilterZip):
    action = 'smudge'


class CleanZip(FilterZip):
    action = 'clean'
