"""
Provides some function to check the latest version of a package on pypi (used
for the plugin manager and the update checker tool).

This functions were extracted from the pip-review tool (from
https://github.com/nvie/pip-tools/blob/master/bin/pip-review).
"""
import json
import os
import re
import sys
import urllib.request as urllib_request

from PyQt5 import QtWidgets
from pkg_resources import parse_version

from hackedit.api import system
from hackedit.api.widgets import DlgRunProcess


def load_pypi_pkg_info(pkg_name):
    if pkg_name is None:
        return

    req = urllib_request.Request(
        'https://pypi.python.org/pypi/{0}/json'.format(pkg_name))
    try:
        handler = urllib_request.urlopen(req)
    except urllib_request.HTTPError:
        return

    if handler.getcode() == 200:
        content = handler.read()
        return json.loads(content.decode('utf-8'))


def guess_pypi_pkg_name(pkg_name):
    req = urllib_request.Request(
        'https://pypi.python.org/simple/{0}/'.format(pkg_name))
    try:
        handler = urllib_request.urlopen(req)
    except urllib_request.HTTPError:
        return None

    if handler.getcode() == 200:
        url_match = re.search(r'/pypi\.python\.org/simple/([^/]+)/',
                              handler.geturl())
        if url_match:
            return url_match.group(1)
    return None


def get_pypi_pkg_version(pkg_name):
    info = load_pypi_pkg_info(pkg_name)
    if info is None:
        guessed_name = guess_pypi_pkg_name(pkg_name)
        if guessed_name is not None:
            info = load_pypi_pkg_info(guessed_name)
    if info is None:
        raise ValueError('Package {0} not found on PyPI.'.format(pkg_name))
    return info['info']['version']


def check_for_update(pkg_name, pkg_version):
    """
    Checks if an update is available for a given package
    """
    try:
        latest_version = get_pypi_pkg_version(pkg_name)
    except ValueError:
        # not available on pypi or connection error, in that case the best
        # is to assume that there is no update.
        return False
    else:
        current = parse_version(pkg_version)
        latest = parse_version(latest_version)
        return latest > current


def graphical_install_package(
        pkg_name, interpreter=sys.executable, parent_window=None,
        autoclose_dlg=False):
    """
    Install a package in the current environment (use it to install
    plugins or to update the application). The process is run graphically
    in a DlgRunProcess dialog.
    """
    if parent_window is None:
        parent_window = QtWidgets.qApp.activeWindow()
    if not os.access(interpreter, os.W_OK):
        pgm = system.get_authentication_program()
        if not pgm:
            raise RuntimeError(
                'No authentification program found' + '\n\n'
                'Please install one of those tools: gksu or kdesu')
        args = ['--', interpreter, '-m', 'pip', 'install', pkg_name,
                '--upgrade']
        if pgm == 'kdesu':
            args.insert(0, '-t')
    else:
        pgm = interpreter
        args = ['-m', 'pip', 'install', pkg_name, '--upgrade']
    return DlgRunProcess.run_process(parent_window, pgm, arguments=args,
                                     autoclose=autoclose_dlg)
