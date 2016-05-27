
from PyQt4 import QtCore
import sys



class StreamSignal(QtCore.QObject):
    '''
    create a connectable stdout instance
    
    to write to the shell and a log file:
    
    >>> import tempfile
    >>> import os
    
    >>> streamOut = StreamSignal('out')
    >>> streamErr = StreamSignal('err')
    
    create a temporary file
    
    >>> (file_id, log_file) = tempfile.mkstemp()
    >>> l = open(log_file, 'w')
    
    connect the stream output to the files-write method
    
    >>> streamOut.message.connect(l.write)
    >>> print 'hello world'
    hello world
    >>> l.close()
    
    check whether the printed message is in the file
    
    >>> l = open(log_file, 'r')
    >>> 'hello world' in l.read()
    True
    >>> l.close()
    '''
    #message = QtCore.Signal(str)# works under pyside
    message = QtCore.pyqtSignal(str)

    def __init__(self, stdout='out', parent=None):
        super(StreamSignal, self).__init__(parent)
        #self.stdout = stdout
#         print 1111, stdout
        if stdout == 'out':
            # save the std output funcs:
            self.stdW = sys.stdout.write
            # forward the std-signals to the new ones:
            sys.stdout = self
        else:
            self.stdW = sys.stderr.write
            sys.stderr = self  
                      
        self._connected = False
        self.setWriteToShell()


    def write(self, message):
        self.message.emit(message)


    def flush(self):
        pass #to prevent errors for sys.stdout.flush()


    def setWriteToShell(self, writeToShell=True):
        '''connect sysout to the qtSignal'''
        if writeToShell and not self._connected:
            self.message.connect(self.stdW) 
            self._connected = True
        elif not writeToShell and self._connected:
            try:
                self.message.disconnect(self.stdW) 
            except TypeError:
                pass #was not connected 
            self._connected = False
            


if __name__ == "__main__":
    import doctest
    doctest.testmod()