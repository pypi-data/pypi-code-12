import subprocess

from ..core import ExternalCommandTask, Task
from ..exceptions import ExternalCommandError
from ..utils import chdir, write_to_tmp_dir
from .basics import walk


class ExternalCommand:
    def __init__(self, cmd):
        self.cmd = cmd
        self.require_empty_stdout = False
        self.require_empty_stderr = False
        self.require_success = False

    def run(self):
        stdin = b''
        with subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            try:
                stdout, stderr = process.communicate(stdin)
            except:
                process.kill()
                process.wait()
                raise

            retcode = process.poll()

            if self.require_empty_stderr:
                if stderr:
                    raise ExternalCommandError(stderr.decode('utf-8'))

            if self.require_empty_stdout:
                if stdout:
                    raise ExternalCommandError(stdout.decode('utf-8'))

            if self.require_success:
                if retcode:
                    raise ExternalCommandError('Command did not exit with success.')

            self.stdout = stdout
            self.stderr = stderr


class babel(ExternalCommandTask):
    """
    Transpiles ES-next to ES-today.

    Available options are modeled after the command line options for the
    ``babel`` command line tool.
    """

    def process(self, inputs):
        cmd = ['babel']
        for t, c, m in inputs:
            yield t, [self.run_external(cmd, input=b''.join(c))], m


class coffee(ExternalCommandTask):
    """Compile Coffeescript to JavaScript."""

    def process(self, inputs):
        for t, c, m in inputs:
            cmd = ['coffee', '--print', '--stdio']
            output = self.run_external(cmd, input=b''.join(c))
            yield t.with_suffix('.js'), [output], m


class traceur(Task):
    """
    Transpiles ES6 JavaScript to ES5.

    Available options are modeled after the command line options for the
    ``traceur`` command line tool.

    Traceur supports two modes: compile as scripts or compile as modules.
    Both patterns are supported.
    """

    def __init__(self, *files,
                 block_binding=None,
                 modules=None,
                 out=None):
        self.block_binding = block_binding
        self.files = files
        self.modules = modules
        self.out = out

    def run_traceur(self):
        # Run traceur
        cmd = ['traceur']
        if self.modules:
            cmd += ['--modules={}'.format(self.modules)]
        if self.block_binding:
            cmd += ['--block-binding=true']
        if self.out:
            cmd += ['--out', self.out]
        if self.files:
            cmd += self.files

        command = ExternalCommand(cmd)
        command.require_empty_stdout = True
        command.require_empty_stderr = True
        command.require_success = True
        command.run()

    def process(self, inputs):
        tmp_dir, paths = write_to_tmp_dir(inputs)
        with chdir(tmp_dir):
            self.run_traceur()
        for t, c, m in walk(tmp_dir):
            if t not in paths:  # filter out any input files, returning only the new files
                yield t, c, m


class uglify(ExternalCommandTask):
    """Minify and obfuscate JavaScript files."""
    def __init__(self, *, compress=True, mangle=True, preamble=None, enclose=False):
        self.compress = compress
        self.enclose = enclose
        self.mangle = mangle
        self.preamble = preamble

    def process(self, inputs):
        for t, c, m in inputs:
            cmd = ['uglifyjs']
            if self.compress:
                cmd += ['--compress']
            if self.mangle:
                cmd += ['--mangle']
            if self.enclose:
                cmd += ['--enclose']
            if self.preamble:
                cmd += ['--preamble', self.preamble]
            output = self.run_external(cmd, input=b''.join(c))
            yield t, [output], m
