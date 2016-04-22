import subprocess
import time
import json
import sys
import os

EXIT_ERROR = 1


class Software:
    """
    The Software object is the main unit in command execution. It is instantiated with a name and
    a path, and commands are executed primarily with the run() method, which takes an arbitrary
    number of Parameter, Redirect, and Pipe objects. Software also takes a single keyword argument,
    shell, which when True will run the command directly on the shell as a string. Shell defaults
    to False for shell injection security reasons.
    """
    def __init__(self, software_name, software_path):
        self.software_name = software_name
        self.software_path = software_path

    def run(self, *args, **kwargs):
        """
        Run this program with Parameters, Redirects, and Pipes. If shell=True, this command is
        executed as a string directly on the shell; otherwise, it's executed using Popen processes
        and appropriate streams.
        :param args: 0 or more of Parameter, Redirect, and Pipe
        :param kwargs: shell=Bool
        :return: None
        """
        # Get default for kwarg shell
        shell = kwargs.get('shell', False)

        # Output log info for this command
        run_cmd = self.__generate_cmd(*args, shell=True)
        sys.stdout.write(' '.join(['>', time.strftime('%d %b %Y %H:%M:%S'), 'Running', self.software_name]) + '\n')
        sys.stdout.write(run_cmd + '\n')

        # If shell is True, execute this command directly as a string
        if shell:
            subprocess.call(run_cmd, shell=True, executable=os.environ['SHELL'])  #TODO Check to see if this works on Windows
        else:
            # Get the command blueprint for this call
            cmd_blueprint = self.__generate_cmd(*args, shell=False)
            output_stream_filehandles = []
            blueprint_processes = []

            # For each command in the blueprint, set up streams and Popen object to execute
            for i, cmd in enumerate(cmd_blueprint):
                stdin_stream = None if i == 0 else blueprint_processes[i - 1].stdout
                stdout_filehandle = None
                stderr_filehandle = None

                # If this comand isn't the last in the list, that means the output
                # is being piped into the next command
                if i + 1 < len(cmd_blueprint):
                    stdout_filehandle = subprocess.PIPE
                # If this is the last command in the list, stdout may be redirected to a file
                elif cmd['stdout']:
                    redir = cmd['stdout']
                    stdout_filehandle = open(redir.dest, redir.mode)
                    output_stream_filehandles.append(stdout_filehandle)

                # stderr can be redirected regardless of piping
                if cmd['stderr']:
                    redir = cmd['stderr']
                    stderr_filehandle = open(redir.dest, redir.mode)
                    output_stream_filehandles.append(stderr_filehandle)

                # Create this process as a Popen object, with appropriate streams
                process = subprocess.Popen(cmd['cmd'], stdin=stdin_stream,
                                 stdout=stdout_filehandle, stderr=stderr_filehandle)
                blueprint_processes.append(process)

                # If this is the last command in the list, wait for it to finish
                if i + 1 == len(cmd_blueprint):
                    process.wait()

            # Close all the file handles created for redirects
            map(lambda f: f.close(), output_stream_filehandles)

    def cmd(self, *args):
        """
        Get this command as a string.
        :param args: 0 or more of Parameter, Redirect, and Pipe
        :return: str Command as a string
        """
        return self.__generate_cmd(*args, shell=True)

    def pipe(self, *args):
        """
        Get a dictionary containing this Software object, as well as the
        arguments passed to this function. This is the method that should be
        called on Software inside a Pipe() argument to another Software.
        :param args: 0 or more of Parameter, Redirect, and Pipe
        :return: dict Dictionary containing this Software object and arguments
        """
        return {
            'software': self,
            'args': args
        }

    def __generate_cmd(self, *args, **kwargs):
        shell = kwargs.get('shell', False)
        # If shell=True, return a full command string
        if shell:
            return '{software_path} {parameters}'.format(
                software_path=self.software_path,
                parameters=' '.join([str(p) for p in args])
            )

        # If shell=False, we have to get much fancier
        def construct_blueprint(blueprint, software_path, args):
            """
            Recursive function meant to construct the command blueprint from a tree of arguments.
            Only called for as many Pipe objects that exist.
            :param blueprint: list Contains commands, passed into itself recursively if necessary
            :param software_path: str Becomes the first item in the list of arguments for Popen
            :param args: list Arguments from which to construct a command
            :return: list All commands generated by this function
            """
            # Break up software call into constituent parts
            cmd_parts = {
                'Parameter': [para for para in args if type(para) == Parameter],
                'Redirect': [redir for redir in args if type(redir) == Redirect],
                'Pipe': [pipe for pipe in args if type(pipe) == Pipe]
            }

            # If there is more than 2 redirects or 1 pipe, ignore extras
            if len(cmd_parts['Redirect']) > 2:
                cmd_parts['Redirect'] = cmd_parts['Redirect'][:2]
            if len(cmd_parts['Pipe']) > 1:
                cmd_parts['Pipe'] = cmd_parts['Pipe'][:1]

            # Set software path and parameters list
            cmd = software_path.split()
            for para in cmd_parts['Parameter']:
                cmd += para.parameters

            # Set appropriate Redirect objects
            stdout, stderr = None, None
            for redir in cmd_parts['Redirect']:
                if redir.stream in Redirect._STDOUT_MODES:
                    stdout = redir
                elif redir.stream in Redirect._STDERR_MODES:
                    stderr = redir
                elif redir.stream in Redirect._BOTH_MODES:
                    stdout, stderr = redir, redir

            # Add this software command to the blueprint
            blueprint.append({
                'cmd': cmd,
                'stdout': stdout,
                'stderr': stderr
            })

            # Recurse if there is a Pipe
            if cmd_parts['Pipe']:
                pipe = cmd_parts['Pipe'][0]
                construct_blueprint(blueprint, pipe.piped_software.software_path, pipe.piped_args)

        # Construct command blueprint and return
        cmd_execution_blueprint = []
        construct_blueprint(cmd_execution_blueprint, self.software_path, args)
        return cmd_execution_blueprint


class Parameter(object):
    """
    The Parameter object abstracts out passing parameters into a Software object.
    """
    def __init__(self, *args):
        self.parameters = args

    def __str__(self):
        return ' '.join(self.parameters)


class Redirect(object):
    """
    The Redirect object abstracts out redirecting streams to files.
    """
    STDOUT = 0
    STDERR = 1
    BOTH = 2
    STDOUT_APPEND = 3
    STDERR_APPEND = 4
    BOTH_APPEND = 5
    NULL = os.devnull
    _APPEND_MODES = [STDOUT_APPEND, STDERR_APPEND, BOTH_APPEND]
    _STDOUT_MODES = [STDOUT, STDOUT_APPEND]
    _STDERR_MODES = [STDERR, STDERR_APPEND]
    _BOTH_MODES = [BOTH, BOTH_APPEND]

    _convert = {
        '>': STDOUT,
        '1>': STDOUT,
        '>>': STDOUT_APPEND,
        '1>>': STDOUT_APPEND,
        '2>': STDERR,
        '2>>': STDERR_APPEND,
        '&>': BOTH,
        '&>>': BOTH_APPEND
    }

    def __init__(self, stream=STDOUT, dest='out.txt'):
        if type(stream) == str:
            stream = Redirect.token_convert(str(stream).strip())

        self.stream = stream
        self.dest = dest
        if stream in Redirect._APPEND_MODES:
            self.mode = 'a'
        else:
            self.mode = 'w'

    def __str__(self):
        return ''.join([Redirect.token_convert(self.stream), self.dest])

    @staticmethod
    def token_convert(token):
        if type(token) == str:
            return Redirect._convert[token]
        elif type(token) == int:
            reverse_convert = {v: k for k, v in Redirect._convert.iteritems()}
            return reverse_convert[token]
        return Redirect.STDOUT


class Pipe(object):
    """
    The Pipe object abstracts out piping the output of one Software into
    the input of another Software. The instantiation argument for Pipe is
    meant to be the result of the Software.pipe() method.
    """
    def __init__(self, piped_software_dict):
        try:
            self.piped_software = piped_software_dict['software']
            self.piped_args = piped_software_dict['args']
        except TypeError as e:
            sys.stderr.write('Software was not piped together correctly\n')
            sys.stderr.write(e.message)

    def __str__(self):
        return '| ' + self.piped_software.cmd(*self.piped_args)


class BasePipeline(object):
    """
    The BasePipeline object is meant to be an abstract class for a Pipeline class. This
    class gives a method for parsing the config file and sets up some necessary
    class variables.
    """
    pipeline_args = None
    pipeline_config = None

    def description(self):
        """
        Override this method.
        A single string describing this pipeline.
        :return: str A description of this pipeline.
        """
        return ''

    def add_pipeline_args(self, parser):
        """
        Override this method.
        Adds arguments to this pipeline using the argparse.add_argument() method. The parser
        argument is an argparse.ArgumentParser() object.
        :param parser: argparse.ArgumentParser object
        :return: argparse.ArgumentParser object, possibly with more arguments
        """
        return parser

    def configure(self):
        """
        Override this method.
        Dictionary representation of the JSON object that will be used to configure this
        pipeline. Configuration variables should be values that will change from platform
        to platform but not run to run, ex. paths to software, but likely not parameters to
        that software.

        Keys will be returned as is, but terminal string values will become input values from
        the user when he/she calls chunky configure.

        In the pipeline, this dictionary will become the class variable pipeline_config, with
        terminal string values replaced with user input values.
        :return: dict Dictionary representation of config values
        """
        return {}

    def run_pipeline(self, pipeline_args, pipeline_config):
        """
        Override this method.
        The logic of the pipeline will be here. The arguments are automatically populated with the
        user arguments to the pipeline (those added with the method add_pipeline_args()) as well as
        the configuration for the pipeline (as a dictionary of the form returned by the method config(),
        but with user input values in place of terminal strings.)
        :param pipeline_args: dict Populated dictionary of user arguments
        :param pipeline_config: dict Populated dictionary of pipeline configuration
        :return: None
        """
        pass

    def _parse_config(self):
        try:
            with open(self.pipeline_args['config']) as config:
                self.pipeline_config = json.loads(config.read())
        except IOError:
            sys.stdout.write('Fatal Error: Config file at {} does not exist.\n'.format(
                self.pipeline_args['config']
            ))
            sys.stdout.write('A config file location can be specified with the --config option.\n')
            sys.exit(EXIT_ERROR)
        except ValueError:
            sys.stdout.write('Fatal Error: Config file at {} is not in JSON format.\n'.format(
                self.pipeline_args['config']
            ))
            sys.exit(EXIT_ERROR)
