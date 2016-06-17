try:
    from mpi4py import MPI
    USING_MPI = MPI.COMM_WORLD.Get_size() > 1
except ImportError:
    USING_MPI = False

from itertools import izip
from logging import StreamHandler
import sys
import traceback
import os
import tempfile

__author__ = 'Ben Kaehler'
__copyright__ = 'Copyright 2016, Ben Kaehler'
__credits__ = ['Ben Kaehler']
__license__ = 'GPLv3 or any later version'
__maintainer__ = 'Ben Kaehler'
__email__ = 'benjamin.kaehler@anu.edu.au'
__status__ = 'Development'
__version__ = '0.0.13-dev'

_DISPATCHER = 0
_WORKTAG = 1
_DIETAG = 2

def am_dispatcher():
    """True if this process is the dispatcher, False if it is a worker """
    return _rank == _DISPATCHER

def rank():
    """The MPI rank of this process"""
    return _rank

def size():
    """The number of MPI processes"""
    return _size

def barrier():
    """All processes must call this method before any will return"""
    if USING_MPI:
        _comm.Barrier()

def checkmakedirs(dirname):
    """Creates the input path if it doesn't exist.

    :param dirname: path to be created
    :type dirname: str

    Checks whether the path exists then creates it if it doesn't. Must be
    called by all MPI processes or it will block. Not safe from race conditions
    if an external influence creates the directory in between the check and the
    creation."""
    if _rank == _DISPATCHER and not os.path.exists(dirname):
        os.makedirs(dirname)
    if USING_MPI:
        _comm.Barrier()

def broadcast(obj):
    """Synchronises the workers' copies of obj to the dispatcher's obj

    :param obj: object to be broadcast
    :type obj: picklable object

    :Example:

    >>> obj = RandomPicklableObject() # all the processes have different objs
    >>> obj = broadcast(obj) # all the processes have a copy of the same obj

    """
    if USING_MPI:
        if _rank != _DISPATCHER:
            obj = None
        return _comm.bcast(obj, root=_DISPATCHER)
    else:
        return obj

def _farm(function, *args):
    """Apply the function to the elements of args, as if they were zipped together.

       :param function: function that takes as many parameters as there are args
       :type function: callable
       :param args: iterables
       :type function: iterable
       :returns: the function results, in random order
       :rtype: iterable

       Distributes the function calls over the workers and makes the results available to
       the dispatcher process as soon as the workers return."""
    if _rank == _DISPATCHER:
        return _dispatcher(i for i in izip(*args))
    else:
        _worker(lambda arg: function(*arg))

def _imap(function, *args):
    """Like :func:`itertools.imap`, but work gets distributed over the workers.
    
    :Example:

    To calculate :math:`\pi` in parallel in (the slow way):

    >>> from random import random
    >>> from mpiutils.dispatcher import imap, am_dispatcher
    >>>
    >>> def am_in_circle(i):
    >>>     x = 2*random() - 1
    >>>     y = 2*random() - 1
    >>>     return x*x + y*y < 1
    >>>
    >>> num_points = 100000
    >>> num_in_circle = 0
    >>> for in_circle in imap(am_in_circle, xrange(num_points)):
    >>>     num_in_circle += in_circle
    >>>
    >>> if am_dispatcher():
    >>> print 4.*num_in_circle/num_points

    """
    def tracker(envelope):
        order, arg = envelope
        return order, function(*arg)
    if _rank == _DISPATCHER:
        cache = {}
        upto = 0
        for order, result in _dispatcher(enumerate(izip(*args))):
            cache[order] = result
            while cache and min(cache) == upto:
                yield cache[upto]
                del cache[upto]
                upto += 1
    else:
        _worker(tracker)
            
def _map(function, *args):
    """Like :func:`map`, but work gets distributed over the workers."""
    return list(_imap(function, *args))

if USING_MPI:
    _comm = MPI.COMM_WORLD
    _rank = _comm.Get_rank()
    _size = _comm.Get_size()
    farm = _farm
    map = _map
    imap = _imap
    exit = _comm.Abort
else:
    _rank = 0
    _size = 1
    map = map
    from itertools import imap
    farm = imap
    exit = sys.exit

def _dispatcher(sequence):
    worker = 0
    for worker, item in enumerate(sequence, _WORKTAG):
        _comm.send(item, dest=worker, tag=_WORKTAG)
        if worker == _size-1:
            outstanding = worker
            break
    else:
        outstanding = worker
        for worker in range(worker+1, _size):
            _comm.send(None, dest=worker, tag=_DIETAG)

    status = MPI.Status()
    for item in sequence:
        result = _comm.recv(source=MPI.ANY_SOURCE, tag=_WORKTAG, status=status)
        worker = status.Get_source()
        _comm.send(item, dest=worker, tag=_WORKTAG)
        yield result

    for i in range(outstanding):
        result = _comm.recv(source=MPI.ANY_SOURCE, tag=_WORKTAG, status=status)
        worker = status.Get_source()
        _comm.send(None, dest=worker, tag=_DIETAG)
        yield result

def _worker(function):
    status = MPI.Status()
    while True:
        item = _comm.recv(source=_DISPATCHER, tag=MPI.ANY_TAG, status=status)
        if status.Get_tag() != _WORKTAG:
            return
        try:
            result = function(item)
        except:
            sys.stderr.write('Uncaught exception:\n'+traceback.format_exc())
            _comm.Abort(1)
        _comm.send(result, dest=_DISPATCHER, tag=_WORKTAG)

def main():
    return 0

if __name__ == '__main__':
    sys.exit(main())
