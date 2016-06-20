#!/usr/bin/env python
import sys
import argparse
from .core import core
from .include import Include


def _primary_opts(parser):
    '''
    Primary command line options, not dependent on input file load.
    '''
    # Version information flag.
    version_kwargs = {
        'action': 'version',
        'version': str('%(prog)s (' + core.get_version() + ')'),
    }
    parser.add_argument('-v', '--version', **version_kwargs)

    # Input file option.
    input_file_kwargs = {
        'type': str,
        'default': core.get_default_input_file(),
        'metavar': 'PATH',
        'help': 'python input file',
    }
    parser.add_argument('-f', '--file', **input_file_kwargs)


def _secondary_opts(parser):
    '''
    Secondary command line options, dependent on input file load.
    '''
    # Logging level option.
    log_level_kwargs = {
        'type': str,
        'default': 'ERROR',
        'metavar': 'LEVEL',
        'help': 'logging level',
    }
    parser.add_argument('-l', '--log-level', **log_level_kwargs)

    # Logging file option.
    log_file_kwargs = {
        'type': str,
        'default': None,
        'help': 'logging file',
    }
    parser.add_argument('--log-file', **log_file_kwargs)


def _target_opts(parser):
    '''
    Target command line options.
    '''
    # Target name and remainder arguments.
    target_kwargs = {
        'nargs': '?',
        'type': str,
        'help': 'target name'
    }
    parser.add_argument('target', **target_kwargs)

    # Target remainder arguments.
    argv_kwargs = {
        'nargs': argparse.REMAINDER,
        'help': 'target arguments'
    }
    parser.add_argument('argv', **argv_kwargs)


def _parse_primary_args(argv):
    '''
    Parse primary options from command line arguments.
    '''
    # Create argument parser and add primary arguments.
    parser = argparse.ArgumentParser(prog=core.get_name(), add_help=False)
    _primary_opts(parser)
    # Add target options to prevent catching target options.
    _target_opts(parser)

    # Parse known arguments, unhandled arguments passed to secondary parser.
    args, discard = parser.parse_known_args(argv)

    # Returns the input file.
    return args.file


def _parse_secondary_args(argv, rules):
    '''
    Parser secondary options from command line arguments.
    '''
    # Construct description from available targets.
    desc = 'available targets: ({0})'.format(', '.join([key for key in rules]))

    # Create argument parser, add primary and secondary arguments.
    parser = argparse.ArgumentParser(prog=core.get_name(), description=desc)
    _primary_opts(parser)
    _secondary_opts(parser)
    _target_opts(parser)

    # Parse all arguments, throw exception on unknown.
    args = parser.parse_args(argv)

    # Internal configuration.
    core.configure_args(args)

    # Return argument parser, target name and remainder arguments.
    return (parser, args.target, args.argv)


def _parse_target_args(target, rule, argv):
    '''
    Parse target command line arguments using options.
    '''
    # Construct program name using target.
    prog = '{0} {1}'.format(core.get_name(), target)

    # Create argument parser for options with target rule description.
    parser = argparse.ArgumentParser(
        prog=prog,
        description=rule.get_description()
    )

    # Add rule options to parser.
    rule.add_options(parser)

    # Parser remainder argumments using constructed parser.
    args = parser.parse_args(argv)

    # Call rule options with parsed arguments.
    rule.call_options(args)


def main(argv=sys.argv[1:],     # Command line arguments excluding script name.
         prog=core.get_name(),  # Default program name.
         stdout=sys.stdout,     # Default output/error streams.
         stderr=sys.stderr):
    '''
    Main command line interface.
    '''
    # Initial internal configuration, sets the program name and stdout/stderr
    # streams for the command line interface.
    core(prog, stdout, stderr)

    # Parse primary command line arguments, this supports the `-f/--file`
    # option to load a specified python input file. If not specified the
    # default input file is imported: `$PWD/faffin.py`.
    input_file = _parse_primary_args(argv)

    # Load available rules from input file using `Include` class.
    Include(input_file)

    # Parse secondary command line arguments, these may depend on rules which
    # have been imported from the input file. Returns the constructed argument
    # parser, target name and remainder arguments.
    parser, target, argv = _parse_secondary_args(argv, Include.get_rules())

    # If target argument specified, call associated rule.
    if target is not None:
        # Get rule from `Include` class, raises exception for unknown target.
        rule = Include.get_rule(target)

        # Target exists, parse target arguments using list of options.
        _parse_target_args(target, rule, argv)

        # Call target rule object.
        updated, total = rule()

        # Report number of targets updated.
        core.write_stdout('`{0}` updated ({1}/{2})'.format(
            target, updated, total
        ))

    # Else display usage information.
    else:
        parser.print_usage()

    return 0
