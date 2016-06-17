import sys
import os
from traceback import format_exc
import logging
from socket import gethostname
import tempfile
from subprocess import Popen, PIPE
import re
from glob import iglob
import shutil

import click

import dispatcher
import mpi_logging

__author__ = 'Ben Kaehler'
__copyright__ = 'Copyright 2016, Ben Kaehler'
__credits__ = ['Ben Kaehler']
__license__ = 'GPLv3 or any later version'
__maintainer__ = 'Ben Kaehler'
__email__ = 'benjamin.kaehler@anu.edu.au'
__status__ = 'Development'
__version__ = '0.0.2-dev'

_versions = {
        'mpimap' : __version__,
        'dispatcher' : dispatcher.__version__,
        'mpi_logging' : mpi_logging.__version__
        }

def setup_logging(log_level, log_file, output_dir):
    try:
        if log_file:
            log_file_dir = os.path.dirname(os.path.abspath(log_file))
            dispatcher.checkmakedirs(log_file_dir)
        else:
            dispatcher.checkmakedirs(output_dir)
            log_file = os.path.join(output_dir, 'log')
        handler = mpi_logging.MPIFileHandler(log_file)
        log_level = getattr(logging, log_level.upper())
        handler.setLevel(log_level)
        hostpid = ''
        if dispatcher.USING_MPI:
            hostpid = gethostname()+':'+str(os.getpid())+':'
        formatter = logging.Formatter('%(asctime)s:'+hostpid+
                '%(levelname)s:%(message)s')
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
        logging.root.setLevel(log_level)
        return log_file
    except:
        sys.stderr.write('Unable to set up logging:\n'+format_exc())
        dispatcher.exit(1)

def detect_input_type(input):
    input_tarred = not os.path.isdir(input)
    input_gzipped = False
    if input_tarred:
        with open(input) as f:
            file_start = f.read(3)
            input_gzipped = file_start == "\x1f\x8b\x08"
    return input_tarred, input_gzipped

def untar(input, output):
    directory = tempfile.mkdtemp()

    def untar_into(tarball, subdir):
        untar_dir = os.path.join(directory, subdir)
        os.mkdir(untar_dir)
        cmd = 'tar', 'xzf', tarball, '-C', untar_dir
        popper = Popen(cmd, stdout=PIPE, stderr=PIPE)
        return_code = popper.wait()
        assert return_code == 0, ' Unable to untar ' + tarball + ':\n' + \
                popper.stdout.read() + popper.stderr.read()
        cmd = 'ls', untar_dir
        popper = Popen(cmd, stdout=PIPE)
        popper.wait()
        tardir = popper.stdout.read().split()
        assert len(tardir) == 1, tarball + ' should contain all its files in '\
                'a single directory'
        return os.path.join(untar_dir, tardir[0])

    try:
        input_dir = untar_into(input, 'input')

        if os.path.exists(output):
            output_dir = untar_into(output, 'output')
        else:
            tardir = os.path.basename(output)
            tardir = tardir[:tardir.find('.ta')]
            output_dir = os.path.join(directory, 'output', tardir)
            os.makedirs(output_dir)
            
        return input_dir, output_dir
    except AssertionError as e:
        sys.stderr.write(e.message+'\n')
        shutil.rmtree(directory)
        dispatcher.exit(1)

def infer_input_pattern(input_pattern, bash_command):
    if input_pattern is None:
        input_pattern = '{}'
        for i, pattern in enumerate(bash_command):
            if '{i}' in pattern:
                input_pattern = pattern.replace('{i}', '{}')
    return input_pattern.replace('{}', '*')

class CommandRunner(object):
    def __init__(self, input_pattern, output_pattern,
            input_dir, output_dir, bash_command, replace):
        self._replace = replace
        self._cmd = list(bash_command)

        self._input_argument = -1
        if input_pattern is None:
            input_pattern = '{}'
            for i, pattern in enumerate(bash_command):
                if '{i}' in pattern:
                    self._input_argument = i
                    input_pattern = pattern.replace('{i}', '{}')
        input_pattern = os.path.join(input_dir, input_pattern)
        input_pattern = re.escape(input_pattern)
        input_pattern = input_pattern.replace(re.escape('{}'), r'(.*)')
        self._input_prog = re.compile(r'\A' + input_pattern + r'\Z')

        self._output_argument = -1
        if output_pattern is None:
            output_pattern = '{}'
            for i, pattern in enumerate(bash_command):
                if '{o}' in pattern:
                    self._output_argument = i
                    output_pattern = pattern.replace('{o}', '{}')
        output_pattern = os.path.join(output_dir, output_pattern)
        self._output_pattern = output_pattern.replace('{}', r'\1')

    def __call__(self, input_file):
        output_file = self._input_prog.sub(self._output_pattern, input_file)
        if os.path.exists(output_file) and not self._replace:
            logging.info('Skipping ' + os.path.basename(input_file) + 
                    ' as output exists')
            return

        if self._input_argument == -1:
            stdin = open(input_file, 'rb')
        else:
            self._cmd[self._input_argument] = input_file
            stdin = PIPE
        if self._output_argument == -1:
            stdout = open(output_file, 'wb')
        else:
            self._cmd[self._output_argument] = output_file
            stdout = PIPE
        popper = Popen(self._cmd, stdin=stdin, stdout=stdout, stderr=PIPE)
        return_code = popper.wait()
        if return_code != 0:
            logging.warning('Got return code ' + str(return_code) + ' for\n' +
                    ' '.join(self._cmd) + ':\n' + popper.stderr.read())
        else:
            logging.info('Mapped ' + os.path.basename(input_file) + ' to ' +
                    os.path.basename(output_file))

def tar(output, output_dir, input_gzipped):
    options = 'czf' if input_gzipped else 'cf'
    output_dir, tar_dir = os.path.split(output_dir)
    cmd = 'tar', options, output, '-C', output_dir, tar_dir
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
    popper = Popen(cmd, stdout=PIPE, stderr=PIPE)
    return_code = popper.wait()
    if return_code != 0:
        sys.stderr.write('Unable to tar results in ' + output_dir + '\n')
        dispatcher.exit(1)
    shutil.rmtree(os.path.dirname(output_dir))

@click.command(context_settings=dict(ignore_unknown_options=True, 
    allow_interspersed_args=False))
@click.option('-i', '--input', required=True, type=click.Path(exists=True),
        help='Input directory or tarball')
@click.option('-o', '--output', required=True, type=click.Path(),
        help='Output directory or tarball')
@click.option('-ip', '--input_pattern', type=str, 
        help='Input filename pattern')
@click.option('-op', '--output_pattern', type=str, 
        help='Output filename pattern')
@click.option('-l', '--log_path', type=click.Path(), help='Log file location')
@click.option('-L', '--log_level', help='Log level', default='INFO',
        type=click.Choice(('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')))
@click.option('--replace/--no_replace', default=False, 
        help='Replace existing output files')
@click.argument('bash_command', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def mpimap(ctx, input, output, input_pattern, output_pattern,
        log_path, log_level, replace, bash_command):
    try:
        # let's save some confusion
        input = os.path.abspath(input)
        output = os.path.abspath(output)

        # untar the input, if necessary
        input_dir = None
        output_dir = None
        if dispatcher.am_dispatcher():
            input_tarred, input_gzipped = detect_input_type(input)
            if input_tarred:
                input_dir, output_dir = untar(input, output)
            else:
                input_dir, output_dir = input, output
        input_dir = dispatcher.broadcast(input_dir)
        output_dir = dispatcher.broadcast(output_dir)

        # set up logging
        setup_logging(log_level, log_path, output_dir)
        if dispatcher.am_dispatcher():
            logging.info(ctx.params)
            logging.info(_versions)

        # do the thing
        command_runner = CommandRunner(input_pattern, output_pattern,
                input_dir, output_dir, bash_command, replace)
        input_pattern = infer_input_pattern(input_pattern, bash_command)
        input_filenames = iglob(os.path.join(input_dir, input_pattern))
        dispatcher.map(command_runner, input_filenames)

        # tar up the output, if necessary
        if dispatcher.am_dispatcher() and input_tarred:
            tar(output, output_dir, input_gzipped)

    except:
        sys.stderr.write('Uncaught exception:\n'+format_exc())
        dispatcher.exit(1)

    return 0

if __name__ == '__main__':
    mpimap()
