import subprocess


class Command(object):
    def __init__(self, command):
        self._command = command

    def execute(self):
        if self._command:
            subprocess.call(self._command, shell=True)
