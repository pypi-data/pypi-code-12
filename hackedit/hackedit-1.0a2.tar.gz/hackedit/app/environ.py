"""
This module contains utility function used for manipulating the process
environment variables.
"""
import json
import os

from PyQt5 import QtCore

from hackedit.api import system


# make sure qt will log to console (especially qfatal output)
os.environ['QT_LOGGING_TO_CONSOLE'] = '1'

if system.DARWIN:
    try:
        path = os.environ['PATH']
    except KeyError:
        path = ''
    paths = ['/bin', '/sbin', '/usr/bin', '/usr/sbin', '/usr/local/bin',
             '/usr/local/sbin', '/opt/bin', '/opt/sbin', '/opt/local/bin',
             '/opt/local/sbin'] + path.split(':')
    os.environ['PATH'] = ':'.join(paths)


def apply():
    """
    Loads environment variables from QSettings and update os.environ
    """
    # update user defined variables
    for k, v in load().items():
        os.environ[k] = v


def restore():
    """
    Restore default environment
    """
    save({})
    apply()


def load():
    """
    Loads environment variables from QSettings
    """
    val = json.loads(QtCore.QSettings().value(
        'env/environment_variables', '{}'))
    return val


def save(env):
    """
    Saves the environement variables dict to QSettings.
    """
    value = json.dumps(env)
    QtCore.QSettings().setValue('env/environment_variables', value)
