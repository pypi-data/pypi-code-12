import glob
import os
import platform
import re
import subprocess
import sys
import tempfile


def detect_system_interpreters():
    """
    Detects system python interpreters
    :return:
    """
    def check_version(path):
        if not os.path.isfile(path):
            return False
        try:
            tmp_dir = os.path.join(tempfile.gettempdir(), 'hackedit')
            try:
                os.makedirs(tmp_dir)
            except OSError:
                pass
            tmp_path = os.path.join(tmp_dir, 'version')
            with open(tmp_path, 'w') as stderr:
                try:
                    output = subprocess.check_output([path, '--version'],
                                                     stderr=stderr).decode()
                except (OSError, subprocess.CalledProcessError):
                    output = ''
            if not output:
                # Python2 print version to stderr (at least on OSX)
                with open(tmp_path, 'r') as stderr:
                    output = stderr.read()
            version = output.split(' ')[1]
        except (IndexError, OSError):
            return False
        else:
            return version > '2.7.0'

    if platform.system().lower() != 'windows':
        executables = []
        for base in ['/usr/bin', '/usr/local/bin',
                     '/usr/opt', '/usr/local/opt']:
            for pth in glob.glob('%s/python*' % base):
                prog = re.compile(r'python[\d.]*$')
                if prog.match(os.path.split(pth)[1]) and check_version(pth):

                    executables.append(os.path.realpath(pth))
    else:
        executables = set()
        executables.add(sys.executable)
        paths = os.environ['PATH'].split(';')
        for path in paths:
            if 'python' in path.lower():
                if 'scripts' in path.lower():
                    path = os.path.abspath(os.path.join(path, os.pardir))
                path = os.path.join(path, 'python.exe')
                if os.path.exists(path):
                    executables.add(path)
    ret_val = sorted(list(set(executables)))
    return ret_val


def is_system_interpreter(path):
    return path in detect_system_interpreters()
