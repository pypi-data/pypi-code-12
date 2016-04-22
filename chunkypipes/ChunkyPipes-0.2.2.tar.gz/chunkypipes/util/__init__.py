import sys
import os
import traceback
from importlib import import_module


def fetch_command_class(subcommand):
    module = import_module('chunkypipes.util.commands.{}'.format(subcommand))
    return module.Command()


def print_no_init():
    sys.stderr.write('ChunkyPipes cannot find an init directory at the user ' +
                     'home or in the CHUNKY_HOME environment variable. Please ' +
                     'run \'chunky init\' before using ChunkyPipes.\n')


def print_help_text():
    fetch_command_class('help').run_from_argv()


def print_unrecognized_command(subcommand):
    sys.stderr.write('Unrecognized command: {}\n\n'.format(subcommand))
    sys.stderr.write('Use one of the following:\n')
    print_help_text()


def add_common_pipeline_args(parser):
    parser.add_argument('--reads', required=True, action='append',
                        help=('Raw reads to process with this pipeline. Paired-end reads ' +
                              'can be joined together with a colon (:). Specify this option ' +
                              'multiple times to process multiple raw reads files.\nEx ' +
                              'paired-end: --reads read1.fastq:read2.fastq\nEx single-end: ' +
                              '--reads sample1.fastq sample1.extra.fastq'))
    parser.add_argument('--output', required=True,
                        help='Directory to store all results of this pipeline in.')
    parser.add_argument('--log')


def execute_from_command_line(argv=None):
    argv = argv or sys.argv[:]
    try:
        subcommand = argv[1]
    except IndexError:
        print_help_text()
        sys.exit(0)

    # chunky_home_root = os.environ.get('CHUNKY_HOME') or os.path.expanduser('~')
    # if not os.path.exists(os.path.join(chunky_home_root, '.chunky')):
    #     print_no_init()
    #     sys.exit(1)

    send_argv = []
    if len(argv) > 2:
        send_argv = argv[2:]

    # Get the class for this called command
    command_class = None
    try:
        command_class = fetch_command_class(subcommand)
    except ImportError:
        print_unrecognized_command(subcommand)

    # Attempt to execute the command
    try:
        command_class.run_from_argv(send_argv)
    except Exception as e:
        sys.stderr.write('ChunkyPipes encountered an error when trying to execute {}:\n'.format(subcommand))
        sys.stderr.write(e.message + '\n')
        traceback.print_exc()
