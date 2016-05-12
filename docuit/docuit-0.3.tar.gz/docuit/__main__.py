#!/home/tw/.local/venvs/pip-tools/bin/python3.5

"""Docuit

Usage:
  docuit (dev|run|test|deploy|build|check) [<file>] [--exec]

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import os
import sys
from subprocess import Popen

from docopt import docopt
from _version import __version__


section_filter = {
    'dev': ['## Dev'],
    'deploy': ['## Deploy', 'Deploy'],
    'run': ['## Run'],
    'test': ['## Test', '## Running the tests'],
    'build': ['## Build']
}


def section(readme_file_name, section, execute):

    processes = []

    with open(readme_file_name) as readme_file:
        started = False
        for line in readme_file:
            if started and line.startswith('#'):
                break

            if started:
                executable = False
                background = False
                statement = line.rstrip('\n').strip()

                if statement.startswith('-'):
                    background = True
                    statement = statement.lstrip('-').strip()
                elif statement.startswith('*'):
                    background = True
                    statement = statement.lstrip('*').strip()

                if len(statement) == 0:
                    continue

                executable = statement[0] == '`'
                command = statement.strip('`')

                print(command)
                if execute and executable:
                    if background:
                        processes.append(
                            Popen(
                                command,
                                stdout=sys.stdout,
                                stderr=sys.stderr,
                                shell=True
                            )
                        )
                    else:
                        os.system(command)
            else:
                for prefix in section_filter[section]:
                    if line.lower().startswith(prefix.lower()):
                        started = True

    for process in processes:
        process.communicate()


def run(readme_file_name, execute):
    section(readme_file_name, 'run', execute)


def test(readme_file_name, execute):
    section(readme_file_name, 'test', execute)


def deploy(readme_file_name, execute):
    section(readme_file_name, 'deploy', execute)


def build(readme_file_name, execute):
    section(readme_file_name, 'build', execute)


def dev(readme_file_name, execute):
    section(readme_file_name, 'dev', execute)


def check(readme_file_name, execute):
    headlines = {}
    with open(readme_file_name) as readme_file:
        for line in readme_file:
            if line.startswith('#'):
                headlines[line.lstrip('#').strip().lower()] = True

    if not headlines.get('deploy'):
        print("Deploy section missing")

    if not headlines.get('test'):
        print("Test section missing")

    if not headlines.get('run'):
        print("Run section missing")
    if not headlines.get('build'):
        print("Build section missing")


def main():
    arguments = docopt(__doc__, version='docuit {}'.format(__version__))

    methods = {
        'dev': dev,
        'run': run,
        'test': test,
        'deploy': deploy,
        'build': build,
        'check': check}

    file_name = arguments.get('<file>')
    if not file_name:
        file_name = 'README.md'

    if not os.path.isfile(file_name):
        sys.exit('No {} found, start with creating it'.format(file_name))

    for method in methods:
        if arguments.get(method):
            return methods[method](file_name, arguments.get('--exec'))


if __name__ == '__main__':
    main()
