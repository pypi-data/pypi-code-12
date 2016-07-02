"""
PyPI tool
"""
import sys
from subprocess import Popen
import distutils.core # pylint: disable=no-name-in-module, import-error
import os
import importlib.machinery
import requests

PYPI_URL = os.environ.get('PYPI_URL', 'https://pypi.python.org/pypi/')
while PYPI_URL.endswith('/'):
    PYPI_URL = PYPI_URL[:-1]

# pylint: disable=no-member

class PatchSetup():
    "Patch Setup is used to get the data which is passed to setup"
    def __init__(self):
        self._restore = [{'obj':distutils.core, 'name':'setup',
                          'value':distutils.core.setup}]
        self.kwargs = None

    def __call__(self, **kwargs):
        self.kwargs = kwargs

    def patcher(self):
        "Mock the setup attributes"
        for kwargs in self._restore:
            setattr(kwargs['obj'], kwargs['name'], self)

    def restore(self):
        "Restore the mocked attributes"
        for kwargs in self._restore:
            setattr(kwargs['obj'], kwargs['name'], kwargs['value'])


def _get_setup_data():
    "Import setup and extract relevant data."
    patch = PatchSetup()
    patch.patcher()
    loader = importlib.machinery.SourceFileLoader('setup', 'setup.py')
    setup = loader.load_module()
    patch.kwargs['__file__'] = setup.__file__
    patch.restore()
    return patch.kwargs

def _get_pypi_info(package):
    "Return the package info."
    tmp = {'releases':dict()}
    url = PYPI_URL
    url = '/'.join([url, package, 'json'])
    got = requests.get(url)
    if got.status_code == 200:
        tmp = got.json()

    return tmp

def _call_setup(*args, cwd='', script='setup.py', sys_mod=sys):
    "Subprocess call"
    env = os.environ.copy()
    env['PYTHONPATH'] = cwd+':'+  env.get('PYTHONPATH', '')
    args = list(args)
    script = os.path.abspath(script)
    args.insert(0, script)
    args.insert(0, sys_mod.executable)
    popen = Popen(args, cwd=cwd, env=env,
                  stderr=sys_mod.stderr, stdout=sys_mod.stdout)
    popen.wait()

def _create_pypirc(path='~/.pypirc'):
    "Create the .pypirc file in the home directory"
    # setuptools is a bit of a closed garden, so reverting back to using as it
    # would be over the command line.
    path = os.path.expanduser(path)

    if os.path.exists(path):
        return (False, path)

    template = (
    "[distutils]\n"
    "index-servers = pypi\n"
    "[pypi]\n"
    "repository=%s\n"
    "username:%s\n"
    "password:%s\n")
    text = template % (PYPI_URL,
                       os.environ['PYPI_USERNAME'],
                       os.environ['PYPI_PASSWORD'])
    with open(path, 'w') as file_write:
        file_write.truncate()
        file_write.write(text)

    return (True, path)

def _valid_version(data, info):
    "Return True if the version can be uploaded."
    if data['version'] in info['releases'].keys():
        text = "# Package '%s' with version '%s' already exists."
        text = text % (data['name'], data['version'])
        print(text)
        return False
    return True

def _clean_up_rc(rc_status):
    "Check if we need to remove the pypi rc file."
    if rc_status[0]:
        os.remove(rc_status[1])

def upload():
    "Build the package and upload to pypi."
    data = _get_setup_data()
    info = _get_pypi_info(data['name'])

    if _valid_version(data, info):
        rc_status = _create_pypirc()
        cwd = os.path.dirname(data['__file__'])
        _call_setup('register', cwd=cwd)
        _call_setup('sdist', 'upload', cwd=cwd)
        _clean_up_rc(rc_status)
        return True

