import os
import sys
import tempfile
import filecmp
import shutil

import click.testing
from mpiutils import mpimap, dispatcher

import data

__author__ = 'Ben Kaehler'
__copyright__ = 'Copyright 2016, Ben Kaehler'
__credits__ = ['Ben Kaehler']
__license__ = 'GPL'
__maintainer__ = 'Ben Kaehler'
__email__ = 'benjamin.kaehler@anu.edu.au'
__status__ = 'Production'
__version__ = '0.0.1-dev'

class _Base(object):
    def setup(self):
        self.tempdir = os.path.join(tempfile.gettempdir(), 'mpimap')

    def teardown(self):
        try:
            shutil.rmtree(self.tempdir)
        except OSError:
            pass


class TestSed(_Base):
    def testSed(self):
        datadir = data.get_data_dir()
        input = os.path.join(datadir, 'tony')
        args = ['-i', input, '-o', self.tempdir, 'sed', 's/Tony/Malcolm/g']
        dispatcher.barrier()
        runner = click.testing.CliRunner()        
        result = runner.invoke(mpimap.mpimap, args)
        dispatcher.barrier()
        assert result.exit_code == 0, 'Non-zero return code'

        output = os.path.join(datadir, 'malcolm')
        dcmp = filecmp.dircmp(output, self.tempdir, ['log'])

        assert len(dcmp.left_only) == 0, 'Files missing from test output'
        assert len(dcmp.diff_files) == 0, 'Some output files different'
        dispatcher.barrier()

class TestGzip(_Base):
    def testGzip(self):
        datadir = data.get_data_dir()
        input = os.path.join(datadir, 'zipped')
        args = ['-i', input, '-o', self.tempdir, 'gzip', '-dc', '{i}.gz']
        dispatcher.barrier()
        runner = click.testing.CliRunner()
        result = runner.invoke(mpimap.mpimap, args)
        dispatcher.barrier()
        assert result.exit_code == 0, 'Non-zero return code'

        output = os.path.join(datadir, 'unzipped')
        dcmp = filecmp.dircmp(output, self.tempdir, ['log'])

        assert len(dcmp.left_only) == 0, 'Files missing from test output'
        assert len(dcmp.diff_files) == 0, 'Some output files different'
        dispatcher.barrier()

class TestCP(_Base):
    def testCP(self):
        datadir = data.get_data_dir()
        input = os.path.join(datadir, 'rst.tar.gz')
        outtar = os.path.join(self.tempdir, 'md.tar.gz')
        input = dispatcher.broadcast(input)
        outtar = dispatcher.broadcast(outtar)
        args = ['-i', input, '-o', outtar, 'cp', '{i}.rst', '{o}.md']
        runner = click.testing.CliRunner()
        dispatcher.barrier()
        result = runner.invoke(mpimap.mpimap, args)
        dispatcher.barrier()
        assert result.exit_code == 0, args

        if dispatcher.am_dispatcher():
            oldtar = os.path.join(datadir, 'md.tar.gz')
            old_dir, test_dir = mpimap.untar(oldtar, outtar)
            dcmp = filecmp.dircmp(old_dir, test_dir, ['log'])

            assert len(dcmp.left_only) == 0, 'Files missing from test output'
            assert len(dcmp.diff_files) == 0, 'Some output files different'
            shutil.rmtree(os.path.dirname(os.path.dirname(old_dir)))
        dispatcher.barrier()

def main():
    testcp = TestCP()
    testcp.setup()
    testcp.testCP()
    testcp.teardown()

if __name__ == '__main__':
    sys.exit(main())
