import sys
import os
import traceback
import argparse
from importlib import import_module

import pkgutil
import chunkypipes.util.commands


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

    # Get command classes
    chunky_command_classes = {chunky_command: fetch_command_class(chunky_command)
                              for chunky_command in [
                                  name for _, name, _
                                  in pkgutil.iter_modules(chunkypipes.util.commands.__path__)
                                  ]
                              }

    # Create subparsers
    parser = argparse.ArgumentParser(prog='chunky')
    subparsers = parser.add_subparsers(dest='subcommand',
                                       metavar='[{}]'.format(', '.join(chunky_command_classes.keys())))

    # Add a subparser for each subcommand
    for chunky_command, chunky_command_class in chunky_command_classes.iteritems():
        subparsers.add_parser(chunky_command, help=chunky_command_class.help_text())

    if len(sys.argv) == 1:
        # If no arguments were given, print help
        parser.print_help()
    else:
        # Otherwise, run subcommand Command class, passing in all arguments after subcommand
        subcommand = vars(parser.parse_args(argv[1:2])).get('subcommand', 'help')
        if subcommand.lower() == 'help':
            parser.print_help()
            sys.exit(0)
        try:
            chunky_command_classes[subcommand].run(argv[2:])
        except Exception as e:
            sys.stderr.write('ChunkyPipes encountered an error when trying to execute {}:\n'.format(subcommand))
            sys.stderr.write(e.message + '\n')
            traceback.print_exc()
