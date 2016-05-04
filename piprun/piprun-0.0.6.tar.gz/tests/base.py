"""Base test classes."""

import os
import traceback
import unittest


class ForkOutputTest(unittest.TestCase):
    """Test functions that start new processes via exec()."""

    def fork_output(self, func):
        """
        Execute a given function in a subprocess and return the output.

        The function result is ignored.
        """

        out_read, out_write = os.pipe()

        if os.fork():
            # Parent process; read from the pipe
            # Close the write end of the pipe so the EOF is received when the
            # child exits
            os.close(out_write)
            with os.fdopen(out_read, 'r') as output:
                return output.read()
        else:
            # Child process; redirect standard output and defer to piprun
            # FIXME: Are stdout and stderr descriptors defined as constants
            # anywhere?
            os.dup2(out_write, 1)
            os.dup2(out_write, 2)
            try:
                func()
            except:  # pylint:disable=bare-except
                traceback.print_exc()
            os._exit(1)  # pylint:disable=protected-access
