"""Piprun main module."""

import os
import subprocess


def devnull():
    """Polyfill subprocess.DEVNULL for Python < 3.3."""
    try:
        return subprocess.DEVNULL
    except AttributeError:
        return open(os.devnull, 'w')


VIRTUALENV_DIR = os.path.expanduser('~/.piprun')


def split_args(args):
    """
    Split an argument list into arguments for piprun itself and the program
    being run. Everything before the first '--' is considered to be
    requirements, what follows '--' is passed to the program. It is an error
    not to have '--' in the list.
    """

    try:
        reqs_end = args.index('--')
    except ValueError:
        raise ValueError("Argument list must include '--'.")

    return args[:reqs_end], args[reqs_end + 1:]


def create_env(path, interpreter, requirements):
    """
    Create a virtual environment.

    :param path: Path of the new virtual environment
    :param interpreter: Python interpreter to use
    :param requirements: Requirements to install into the environment
    """

    virtualenv_args = ['virtualenv', '--quiet']
    if interpreter:
        virtualenv_args.append('--python={}'.format(interpreter))
    virtualenv_args.append(path)
    subprocess.check_call(virtualenv_args, stdout=devnull())

    pip = os.path.join(path, 'bin', 'pip')
    subprocess.check_call((pip, 'install') + requirements,
                          stdout=devnull())


def activate_env(path):
    """Set environment variables to activate the virtual environment."""

    os.environ['VIRTUAL_ENV'] = path

    old_path = os.environ.get('PATH', '')
    env_bin = os.path.join(path, 'bin')
    os.environ['PATH'] = env_bin + ':' + old_path


def main(*args):
    """Main entry point."""

    requirements, args = split_args(args)

    if os.path.exists(requirements[0]):
        interpreter = requirements[0]
        requirements = requirements[1:]
    else:
        interpreter = None

    requirements_hash = str(hash((interpreter, requirements)))

    env_path = os.path.join(VIRTUALENV_DIR, requirements_hash)

    if not os.path.exists(env_path):
        create_env(
            env_path,
            interpreter=interpreter,
            requirements=requirements,
        )

    activate_env(env_path)

    env_python = os.path.join(env_path, 'bin', 'python')
    os.execv(env_python, (env_python,) + args)
