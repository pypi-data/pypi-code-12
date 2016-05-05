#!/usr/bin/env python
from pathlib import Path
from collections import defaultdict
import os
import subprocess
from string import Template
from .command import Command
from matador.session import Session


def _command_condition(*args):
    """

    Parameters
    ----------
    args: list
        containing boolean values for:
            if a command has been specified explicitly
            if the dbms is oracle
            if the os is posix
            if windows authentication has been specified

    Returns
    -------
        tuple of values which can be used to determine the appropriate command
        to run an sql script

    """
    try:
        most_significant_argument = args.index(True)
    except ValueError:
        most_significant_argument = -1

    conditions = {
        0: ('command'),
        1: ('oracle'),
        2: ('mssql', 'posix'),
        3: ('mssql', 'nt', 'windows_authentication'),
        -1: ('mssql', 'nt', 'mssql_authentication')
    }

    return conditions[most_significant_argument]


def _command(**kwargs):
    """
    Parameters
    ----------
    kwargs : dict
        A dictionary containing values for:
            command (optional, overrides all other entries)
            dbms
            client_os
            server
            db_name
            port (Oracle only)
            windows_authentication (MSSQL on windows clients only)
            user
            password
    """
    command_condition = _command_condition(
        'command' in kwargs,
        kwargs['dbms'].lower() == 'oracle',
        kwargs['client_os'] == 'posix',
        'windows_authentication' in kwargs)

    # Create a default dictionary based on kwargs but with any missing
    # keys returning an empty string.
    params = defaultdict(str, kwargs)

    commands = {
        ('command'):
            params['command'],
        ('oracle'):
            'sqlplus -S -L ${user}/${password}@${server}:${port}/${db_name}',
        ('mssql', 'posix'):
            'bsqldb -S ${server} -D ${db_name} -U ${user} -P ${password}',
        ('mssql', 'nt', 'windows_authentication'):
            'sqlcmd -S ${server} -d ${db_name} -E',
        ('mssql', 'nt', 'mssql_authentication'):
            'sqlcmd -S ${server} -d ${db_name} -U ${user} -P ${password}'
    }

    return Template(commands[command_condition]).substitute(params)


def _sql_script(**kwargs):
    """
    Parameters
    ----------
    kwargs : dict
        A dictionary containing values for:
            dbms
            directory
            file
    """
    file = Path(kwargs['directory'], kwargs['file'])

    with file.open('r') as f:
        script = f.read()
        f.close()

    if kwargs['dbms'] == 'oracle':
        script += '\nshow error'

    return script.encode('utf-8')


def run_sql_script(logger, **kwargs):
    """
    Parameters
    ----------
    kwargs : dict
        A dictionary containing values for:
            dbms
            server
            db_name
            directory
            file
    """
    message = Template(
        'Matador: Executing ${file} against ${db_name} on ${server} \n')
    logger.info(message.substitute(kwargs))
    kwargs['client_os'] = os.name

    os.chdir(kwargs['directory'])

    process = subprocess.Popen(
        _command(**kwargs).split(),
        stdin=subprocess.PIPE)
    process.stdin.write(_sql_script(**kwargs))
    process.stdin.close()
    process.wait()


class RunSqlScript(Command):

    def _add_arguments(self, parser):

        parser.add_argument(
            '-d', '--directory',
            type=str,
            required=True,
            help='Directory containing script')

        parser.add_argument(
            '-f', '--file',
            type=str,
            required=True,
            help='Script file name')

        parser.add_argument(
            '-e', '--environment',
            type=str,
            required=True,
            help='Agresso environment')

    def _execute(self):
        Session.set_environment(self.args.environment)
        kwargs = {
            **Session.environment['database'],
            **Session.credentials,
            **self.args.__dict__}
        run_sql_script(self._logger, **kwargs)
