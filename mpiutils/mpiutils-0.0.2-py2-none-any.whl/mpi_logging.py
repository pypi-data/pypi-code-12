try:
    from mpi4py import MPI
except ImportError:
    pass
from dispatcher import USING_MPI, am_dispatcher
from logging import StreamHandler

__author__ = 'Ben Kaehler'
__copyright__ = 'Copyright 2016, Ben Kaehler'
__credits__ = ['Ben Kaehler']
__license__ = 'GPLv3 or any later version'
__maintainer__ = 'Ben Kaehler'
__email__ = 'benjamin.kaehler@anu.edu.au'
__status__ = 'Development'
__version__ = '0.0.1-dev'

def _open(filename, mode='a'):
    """Create an MPI safe file object for use with logging.StreamHandler"""
    return _file(filename, mode=mode)

class _file(object):
    """Only intended to fulfill the requirements of logging.StreamHandler"""
    def __init__(self, filename, mode='a'):
        if mode not in 'aw':
            raise ValueError(mode+' is not a valid mode for this log file')
        filemode = MPI.MODE_CREATE | MPI.MODE_WRONLY
        if 'a' in mode:
            filemode |= MPI.MODE_APPEND
        self._am_open = True
        self._stream = MPI.File.Open(_comm, filename, filemode)
        if 'a' not in mode: # MPI.File.Open never truncates
            self._stream.Set_size(0)
            _comm.Barrier()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def write(self, b):
        self._stream.Write_shared(b.encode('utf-8')) # unicode crashes mpi4py

    def flush(self):
        self._stream.Sync()

    def close(self):
        _comm.Barrier() # make sure everyone agrees
        self._stream.Close()

if USING_MPI:
    _comm = MPI.COMM_WORLD
    open = _open
    file = _file
else:
    open = open
    file = file

class MPIFileHandler(StreamHandler):
    """An MPI-safe :code:`logging.StreamHandler`.

    :Example:

    >>> handler = MPIFileHandler(log_file)
    >>> handler.setLevel(logging.INFO)
    >>> hostpid = socket.gethostname()+':'+str(os.getpid())+':'
    >>> formatter = logging.Formatter('%(asctime)s:'+hostpid+
    >>>         '%(levelname)s:%(message)s')
    >>> handler.setFormatter(formatter)
    >>> logging.root.addHandler(handler)
    >>> logging.root.setLevel(log_level)
    """
    def __init__(self, filename, filemode='a'):
        self._file = open(filename, filemode)
        super(MPIFileHandler, self).__init__(self._file)

    def close(self):
        super(MPIFileHandler, self).close()
        self._file.close()

