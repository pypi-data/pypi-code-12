from __future__ import absolute_import
from copy import deepcopy
from contextlib import contextmanager

import errno
import logging
from logging.config import dictConfig as logConfig

import json
import os
from os.path import (
    abspath,
    expanduser,
    isabs,
    isdir,
    join as path_join,
    exists as path_exists,
)

import stat
import subprocess
import time
import tempfile
from six.moves.urllib.error import (
    HTTPError,
    URLError,
)
from six.moves.urllib.request import (
    urlopen,
)
import zipfile
import six

try:
    from yaml import CSafeLoader, CSafeDumper
    SafeLoader, SafeDumper = CSafeLoader, CSafeDumper
except ImportError:
    from yaml import SafeLoader

import yaml


class ErrorExit(Exception):

    def __init__(self, error=None):
        self.error = error


class DeploymentError(Exception):
    """One or more errors occurred during the deployment preparation."""

    def __init__(self, errors):
        self.errors = errors
        super(DeploymentError, self).__init__(errors)

    def __str__(self):
        return '\n'.join(self.errors)


STORE_URL = "https://api.jujucharms.com/charmstore"


# Utility functions
def yaml_dump(value):
    return yaml.dump(value, default_flow_style=False)


def yaml_load(value):
    return yaml.load(value, Loader=SafeLoader)


# We're not using safe dumper because we're using other custom
# representers as well.
def _unicode_representer(dumper, uni):
    node = yaml.ScalarNode(tag=u'tag:yaml.org,2002:str', value=uni)
    return node

yaml.add_representer(six.text_type, _unicode_representer)


DEFAULT_LOGGING = """
version: 1
formatters:
    standard:
        format: '%(asctime)s %(message)s'
        datefmt: "%Y-%m-%d %H:%M:%S"
    detailed:
        format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        datefmt: "%Y-%m-%d %H:%M:%S"
handlers:
    console:
        class: logging.StreamHandler
        formatter: standard
        level: DEBUG
        stream: ext://sys.stderr
loggers:
    deployer:
        level: INFO
        propogate: true
    deploy.cli:
        level: DEBUG
        propogate: true
    deploy.charm:
        level: DEBUG
        propogate: true
    deploy.env:
        level: DEBUG
        propogate: true
    deploy.deploy:
        level: DEBUG
        propogate: true
    deploy.importer:
        level: DEBUG
        propogate: true
    "":
        level: INFO
        handlers:
            - console
"""


def setup_logging(verbose=False, debug=False, stream=None):
    config = yaml_load(DEFAULT_LOGGING)
    log_options = {}
    if verbose:
        log_options.update({"loggers": {
            "deployer": {"level": "DEBUG", "propogate": True}}})
    if debug:
        log_options.update(
            {"handlers": {"console": {"formatter": "detailed"}}})
    config = dict_merge(config, log_options)
    logConfig(config)

    # Allow tests to reuse this func to mass configure log streams.
    if stream:
        root = logging.getLogger()
        previous = root.handlers[0]
        root.handlers[0] = current = logging.StreamHandler(stream)
        current.setFormatter(previous.formatter)
        return stream


@contextmanager
def temp_file():
    t = tempfile.NamedTemporaryFile()
    try:
        yield t
    finally:
        t.close()


def extract_zip(zip_path, dir_path):
    zf = zipfile.ZipFile(zip_path, "r")
    for info in zf.infolist():
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            source = zf.read(info.filename)
            target = os.path.join(dir_path, info.filename)
            if os.path.exists(target):
                os.remove(target)
            os.symlink(source, target)
            continue
        extract_path = zf.extract(info, dir_path)
        os.chmod(extract_path, mode)


UNITS_DICT = {
    'M': 1,
    'G': 1024,
    'T': 1024 * 1024,
    'P': 1024 * 1024 * 1024,
}


def _to_number(value):
    """Convert a string to a numeric.

    The returned value is either an int or a float, depending on the input.
    Raises a ValueError if the value cannot be parsed.
    """
    try:
        num = int(value)
    except ValueError:
        num = float(value)
    return num


def _convert_units_specifier(value):
    """Convert a string that may have a unit specifier.

    Given a string possibly containing a unit specifier, return the
    the string representing the number and the units multiplier.
    """
    units = UNITS_DICT.get(value[-1], None)
    if units is not None:
        value = value[:-1]
    else:
        units = 1
    return value, units


def parse_constraints(value):
    """Parse the constraints, converting size specifiers into ints.

    Specifiers of 'M' and 'G' are supported.  The resulting value is the number
    of megabytes.

    The input is either a string of the form "k1=v1 ... kn=vn" or a dictionary.
    """
    if value is None:
        return value
    constraints_with_units = ['mem', 'root-disk']
    numerics = ['cpu-cores', 'cpu-power'] + constraints_with_units
    lists = ['tags']
    constraints = {}
    if isinstance(value, dict):
        constraints.update(value)
    else:
        pairs = value.strip().split()
        for item in pairs:
            k, v = item.split('=')
            constraints[k] = v

    for k, v in constraints.items():
        if k in lists:
            v = v.split(',')
        elif k in numerics:
            # Currently numeric constraints are never passed as slices. For
            # this reason, it is safe to assume that a numeric value is always
            # a string and never a list.
            units = 1
            if k in constraints_with_units:
                v, units = _convert_units_specifier(v)
            try:
                v = _to_number(v) * units
            except ValueError:
                raise ValueError(
                    'Constraint {} has invalid value {}'.format(
                        k, constraints[k]))
        constraints[k] = v
    return constraints


def _get_juju_home():
    if get_juju_major_version() == 1:
        return (
            os.environ.get("JUJU_HOME") or
            path_join(os.environ.get('HOME'), '.juju')
        )
    return (
        os.environ.get("JUJU_DATA") or
        path_join(os.environ.get('HOME'), '.local', 'share', 'juju')
    )


_juju_major_version = None


def get_juju_major_version():
    global _juju_major_version
    if _juju_major_version is None:
        log = logging.getLogger("deployer.utils")
        _juju_major_version = int(_check_call(
            ["juju", "--version"], log).split(b'.')[0])
    return _juju_major_version


def get_juju_default_env():
    if get_juju_major_version() == 1:
        return os.environ.get("JUJU_ENV")
    else:
        return os.environ.get("JUJU_MODEL")


def _check_call(params, log, *args, **kw):
    max_retry = kw.get('max_retry', None)
    cur = kw.get('cur_try', 1)
    shell = kw.get('shell', False)
    try:
        cwd = abspath(".")
        if 'cwd' in kw:
            cwd = kw['cwd']
        stderr = subprocess.STDOUT
        if 'stderr' in kw:
            stderr = kw['stderr']
        output = subprocess.check_output(
            params, cwd=cwd, stderr=stderr, env=os.environ, shell=shell)
    except subprocess.CalledProcessError as e:
        if 'ignoreerr' in kw:
            return
        log.error(*args)
        log.error("Command (%s) Output:\n\n %s", " ".join(params), e.output)
        if not max_retry or cur > max_retry:
            raise ErrorExit(e)
        kw['cur_try'] = cur + 1
        log.error("Retrying (%s of %s)" % (cur, max_retry))
        time.sleep(1)
        output = _check_call(params, log, args, **kw)
    return output


# Utils from deployer 1
def relations_combine(onto, source):
    target = deepcopy(onto)
    # Support list of relations targets
    if isinstance(onto, list) and isinstance(source, list):
        target.extend(source)
        return target
    for (key, value) in source.items():
        if key in target:
            if isinstance(target[key], dict) and isinstance(value, dict):
                target[key] = relations_combine(target[key], value)
            elif isinstance(target[key], list) and isinstance(value, list):
                target[key] = list(set(target[key] + value))
        else:
            target[key] = value
    return target


def dict_merge(onto, source):
    target = deepcopy(onto)
    for (key, value) in source.items():
        if key == 'relations' and key in target:
            target[key] = relations_combine(target[key], value)
        elif (key in target and isinstance(target[key], dict) and
                isinstance(value, dict)):
            target[key] = dict_merge(target[key], value)
        else:
            target[key] = value
    return target


def resolve_include(fname, include_dirs):
    if isabs(fname):
        return fname
    for path in include_dirs:
        full_path = path_join(path, fname)
        if path_exists(full_path):
            return full_path

    return None


def mkdir(path):
    """Create a leaf directory and all intermediate ones.

    Also expand ~ and ~user constructions.
    If path exists and it's a directory, return without errors.
    """
    path = expanduser(path)
    try:
        os.makedirs(path)
    except OSError as err:
        # Re-raise the error if the target path exists but it is not a dir.
        if (err.errno != errno.EEXIST) or (not isdir(path)):
            raise


def _is_qualified_charm_url(url):
    """Test an URL to see if it is revisioned."""
    parts = url.rsplit('-', 1)
    return len(parts) > 1 and parts[-1].isdigit()


def get_qualified_charm_url(url):
    """Given a charm URL, if not revisioned, return the latest revisioned URL.

    If the URL is already revisioned, return it.
    Otherwise ask the Charm store for the latest revision and return that URL.
    """
    if _is_qualified_charm_url(url):
        return url
    info_url = "%s/charm-info?charms=%s" % (STORE_URL, url)
    try:
        fh = urlopen(info_url)
    except (HTTPError, URLError) as e:
        errmsg = '{} ({})'.format(e, info_url)
        raise DeploymentError([errmsg])
    content = json.loads(fh.read().decode())
    rev = content[url]['revision']
    return "%s-%d" % (url, rev)


def get_env_name(param_env_name):
    """Get the environment name.

    """
    if param_env_name:
        return param_env_name
    elif get_juju_default_env():
        return get_juju_default_env()

    if get_juju_major_version() == 1:
        juju_home = _get_juju_home()
        env_ptr = os.path.join(juju_home, "current-environment")
        if os.path.exists(env_ptr):
            with open(env_ptr) as fh:
                return fh.read().strip()

        with open(os.path.join(juju_home, 'environments.yaml')) as fh:
            conf = yaml_load(fh.read())
            if 'default' not in conf:
                raise ValueError("No Environment specified")
            return conf['default']
    else:
        # Return the juju2 controller:model combo
        log = logging.getLogger("deployer.utils")
        return _check_call(["juju", "switch"], log).strip().decode()


def x_in_y(x, y):
    """Check to see if the second argument is named in the first
    argument's unit placement spec.

    Both arguments provided are services with unit placement directives.
    If the first service appears in the second service's unit placement,
    either colocated on a default unit, colocated with a specific unit,
    or containerized alongside that service, then True is returned, False
    otherwise.
    """
    for placement in y.unit_placement:
        if ':' in placement:
            _, placement = placement.split(':')
        if '/' in placement:
            placement, _ = placement.split('/')
        if x.name == placement:
            return True
    return False
