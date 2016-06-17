from nose.tools import assert_in, assert_equal
from tempfile import gettempdir
import logging
from socket import gethostname
from shutil import rmtree
import os
import sys

from mpiutils import dispatcher
from mpiutils import mpi_logging

class TestIO(object):
    def setup(self):
        self.tempdir = os.path.join(gettempdir(), 'test_io')
        dispatcher.checkmakedirs(self.tempdir)
        self.tempfilename = os.path.join(self.tempdir, 'tempfile')

    def teardown(self):
        try:
            rmtree(self.tempdir)
        except OSError:
            pass

    def test_io(self):
        tempfilename = self.tempfilename
        tempfile = mpi_logging.open(tempfilename, mode='w')
        tempfile.write(str(dispatcher.rank())+'\n')
        tempfile.flush()
        contents = ''
        with open(tempfilename) as stillopen:
            contents = stillopen.read()
        assert_in(str(dispatcher.rank())+'\n', contents)
        tempfile.close()
        with open(tempfilename) as nowclosed:
            ranks = [int(s.strip()) for s in nowclosed]
        assert_equal(set(ranks), set(range(dispatcher.size())))
        tempfile = mpi_logging.open(tempfilename, 'a')
        tempfile.write(str(dispatcher.rank())+'\n')
        tempfile.close()
        with open(tempfilename) as nowclosed:
            ranks = [int(s.strip()) for s in nowclosed]
        assert_equal(len(ranks), dispatcher.size()*2)
        assert_equal(set(ranks), set(range(dispatcher.size())))
        if dispatcher.size() != 1:
            dispatcher._comm.Barrier()

class TestMPIFileHandler(object):
    def setup(self):
        self.tempdir = os.path.join(gettempdir(), 'test_MPIFileHandler')
        dispatcher.checkmakedirs(self.tempdir)
        self.tempfilename = os.path.join(self.tempdir, 'tempfile')

    def teardown(self):
        try:
            rmtree(self.tempdir)
        except OSError:
            pass

    def test_MPIFileHandler(self):
        tempfilename = self.tempfilename
        handler = mpi_logging.MPIFileHandler(tempfilename, 'w')
        host = gethostname()
        formatter = logging.Formatter(host+':%(message)s')
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
        logging.warn('TEST')
        logging.getLogger().removeHandler(handler)
        handler.flush()
        handler.close()
        lines = {}
        with open(tempfilename) as tempfile:
            lines = set(tempfile.readlines())
        assert_equal(lines, set([host+':TEST\n']))
        if dispatcher.size() != 1:
            dispatcher._comm.Barrier()


def main():
    tester = TestIO()
    tester.setup()
    try:
        tester.test_io()
    finally:
        tester.teardown()
    tester = TestMPIFileHandler()
    tester.setup()
    try:
        tester.test_MPIFileHandler()
    finally:
        tester.teardown()

if __name__ == '__main__':
    sys.exit(main())

