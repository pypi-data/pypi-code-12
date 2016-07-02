import datetime
import sys
from traceback import format_exception

from .Importer.QtCore import *



class Debug(QObject):
    """Simple debug output class, accepts debug strings and displays them or otherwise
    depending on options"""
    updated = Signal(str)
    def __init__(self):
        QObject.__init__(self)
        self.enabled = True
        self.pdb = False
        self.log = []
        sys.excepthook = self.excepthook

    def excepthook(self, t, v, e):
        self.debug("\n" + "".join(format_exception(t, v, e)), silent=True)
        if not self.pdb:
            sys.__excepthook__(t, v, e)
        else:
            # start debugger
            import pdb
            self.debug("STARTING PDB\n")
            pdb.pm()

    def debug(self, *message, **kwargs):
        msg = datetime.datetime.now().strftime("[%H:%M:%S] ") + " ".join(str(i) for i in message)
        if (not "silent" in kwargs) & (self.enabled):
            try:
                sys.stderr.write(msg + "\n")
            except IOError:
                # apparently this is occasionally, but not always(!?), thrown
                # on Windows when running with no console. in this case it
                # doesn't matter, since only the debug widget will ever be
                # read.
                pass
        self.log.append(msg)
        self.updated.emit(msg)

debug = Debug()
