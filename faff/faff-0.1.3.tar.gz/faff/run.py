#!/usr/bin/env python
import sys
import subprocess
from .main import core
from .variable import Variable


class Run(object):
    '''
    Run command class.
    '''
    def __init__(self, cmd, cwd, output=None, text=None):
        # Call self with arguments.
        self(cmd, cwd, output, text)

    def __call__(self, cmd, cwd, output, text):
        # Debug command before variable expansion.
        core.debug(__name__, cmd)

        # Format command string using variables.
        cmd = Variable.expand(cmd)

        # Write the expanded command to stdout.
        core.write_stdout(cmd)
        # If command override text provided, display it now.
        if text is not None:
            core.write_stdout(text)

        # Run command as subprocess, capture stdout/stderr. This may raise
        # exceptions which are caught by the caller, usually `_Rule` class.
        try:
            proc = subprocess.run(
                cmd.split(' '),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
            )

            # Default to UTF-8 encoding if none available.
            enc = sys.stdout.encoding
            if enc is None:
                enc = 'UTF-8'

            # Decode process output for display.
            out = proc.stdout.decode(enc)

        # Python 2.x subprocess module doesn't have `run` or encoding related
        # functions, fallback on `check_output`.
        except AttributeError:
            out = subprocess.check_output(
                cmd.split(' '),
                stderr=subprocess.STDOUT,
                cwd=cwd,
            )

        # If output file argument given, write to file.
        if output is not None:
            with open(output, 'w') as f:
                f.write(out)

        # Else if command override text not provided, display on stdout.
        elif text is None:
            core.write_stdout(out, raw=True)
