#!/usr/bin/env python
from pathlib import Path
import os
import subprocess
from string import Template
from .command import Command
from matador.session import Session


def _command(**kwargs):
    """
    Parameters
    ----------
    kwargs : dict
        A dictionary containing values for:
            user
            password
            server
            port (optional, for Oracle only)
            db_name
    """
    oracle_connection = Template(
        '${user}/${password}@${server}:${port}/${db_name}')

    commands = {
        ('oracle', 'nt'): [
            'sqlplus', '-S', '-L', oracle_connection.substitute(kwargs)],
        ('mssql', 'posix'): [
            'bsqldb', '-S', kwargs['server'],
            '-D', kwargs['db_name'], '-U', kwargs['user'],
            '-P', kwargs['password']
        ],
        ('mssql', 'nt'): [
            'sqlcmd', '-S', kwargs['server'],
            '-d', kwargs['db_name'], '-U', kwargs['user'],
            '-P', kwargs['password']
        ],
    }
    commands[('oracle', 'posix')] = commands[('oracle', 'nt')]

    return commands[(kwargs['dbms'], os.name)]


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

    os.chdir(kwargs['directory'])

    process = subprocess.Popen(
        _command(**kwargs),
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
