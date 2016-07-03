# pypimonitor — An HTML dashboard to monitor your python packages
# Copyright (C) 2016 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Gather data about packages, and render them as an HTML page."""

import colorsys
import datetime
import functools
import itertools
import json
import logging
import operator
import os
import random
import sys
import urllib
import xmlrpc.client as xmlrpclib
import yaml

import jinja2
import pkg_resources
import requests

from pypimonitor.cell import load_cell_plugins
from pypimonitor.cell.base import Error

VERSION = "0.2.0"
LOGGER = logging.getLogger(__name__)

CLIENT = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')

class Counter:
    """Each call to :meth:`Counter.count` increments a counter, and return its value."""
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.value = 0

    def count(self):
        """Increments counter, and return counter value."""
        self.value += 1
        return self.value

def random_color(seed, saturation, value):
    """Return a pseudo-random color."""
    old_seed = random.random()
    random.seed(seed)
    rgb = colorsys.hsv_to_rgb(random.random(), saturation, value)
    random.seed(old_seed)
    return "#%02x%02x%02x" % tuple([int(value * 255) for value in rgb])

def iter_user_packages(user):
    """Iterate over packages owned by a given user."""
    for _, package in CLIENT.user_packages(user):
        yield package

class Renderer:
    """Get information about packages, and produce an HTML dashboard to monitor them."""

    def __init__(self, config, form=None):
        self.errors = set()

        # Processing config
        self.config = config
        if "cells" not in self.config:
            self.config['cells'] = list(set(itertools.chain(*[
                package.keys()
                for package
                in self.config['packages'].values()
                ])))
        for package in self.config['packages']:
            if self.config['packages'][package] is None:
                self.config['packages'][package] = {}
            for cell in self.config['cells']:
                if self.config['packages'][package].get(cell, None) is None:
                    self.config['packages'][package][cell] = {}
                # Set default values
                for key in self.config.get('default', {}):
                    if key not in self.config['packages'][package]:
                        self.config['packages'][package][key] = self.config['default'][key]
                if 'cell' not in self.config['packages'][package][cell]:
                    self.config['packages'][package][cell]['cell'] = cell

        # Processing packages
        self.packages = {}
        for name in sorted(config['packages']):
            try:
                self.packages[name] = Package(name)
            except Exception as error: # pylint: disable=broad-except
                self.log_error("Ignoring package '{}': {}".format(name, error))
                continue

        # Processing form
        self.form = form
        if self.form is not None:
            for key in ['pkg', 'user', 'col']:
                self.form[key] = ",".join(set(
                    itertools.chain(*[item.split(",") for item in self.form.get(key, [])])
                ))

        # Loading plugins
        self.cells = {
            plugin.keyword: plugin(self)
            for plugin
            in load_cell_plugins()
            }
        self.cells['error'] = Error(self)

    @classmethod
    def from_yaml(cls, filename, form=None):
        """Factory to return a :class:`Renderer` from a yaml file."""
        with open(filename, 'r') as stream:
            return cls(yaml.safe_load(stream.read()), form=form)

    @classmethod
    def from_args(cls, packages=None, cells=None, users=None, form=None):
        """Factory to return a :class:`Renderer` from list of arguments."""
        config = {}

        # Processing packages
        if packages is None:
            packages = []
        packages = list(itertools.chain(*[item.split(",") for item in packages]))
        if users is not None:
            for user in users:
                try:
                    packages.extend(iter_user_packages(user))
                except urllib.error.HTTPError as error:
                    LOGGER.error("Ignoring user '{}': {}".format(
                        user,
                        str(error),
                        ))
        packages = list(set(packages))
        config['packages'] = {pkg: {} for pkg in set(packages)}

        # Processing cells
        if cells is None:
            cells = []
        cells = list(itertools.chain(*[item.split(",") for item in cells]))
        if cells:
            config['cells'] = cells

        return cls(config, form=form)

    def __iter__(self):
        """Return iterator to `self.packages`."""
        yield from self.packages

    def values(self):
        """Yield `self.packages` values."""
        yield from self.packages.values()

    def __getitem__(self, key):
        return self.packages[key]

    @staticmethod
    def _get_environment():
        templatedir = os.path.join(
            pkg_resources.resource_filename(__name__, 'data'),
            'templates',
            )

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(templatedir))
        env.globals['counter'] = Counter().count
        env.globals['now'] = datetime.datetime.now()
        env.filters['datetime'] = operator.methodcaller('strftime', "%Y-%m-%d %H:%M:%S")
        env.filters['color'] = random_color
        return env

    def render(self):
        """Return the HTML code."""
        return self._get_environment().get_template("index.html").render( # pylint: disable=no-member
            config=self.config,
            cells=self.cells,
            packages=self.packages,
            form=self.form,
            errors=self.errors,
            version=VERSION,
            )

    def log_error(self, message):
        """Log error, both to HTML page and console."""
        LOGGER.error(message)
        self.errors.add(message)


class Package:
    """Gather information about a single package."""
    # pylint: disable=too-few-public-methods

    def __init__(self, name):
        LOGGER.info("Retrieving information about pypi package '{}'...\n".format(name))
        try:
            self.rawdata = json.loads(
                requests.get(
                    "http://pypi.python.org/pypi/{}/json".format(name)
                    ).text
                )
        except Exception as error:
            raise Exception("Error while getting data for package '{}': {}.".format(name, error))
        self.name = name
        self.info = self.rawdata["info"]
        self.releases = {}
        for version, files in self.rawdata['releases'].items():
            if not files:
                continue
            date = datetime.datetime.strptime(
                min((url['upload_time'] for url in files)),
                "%Y-%m-%dT%H:%M:%S",
                )
            self.releases[date] = {}
            self.releases[date]['downloads'] = sum((url['downloads'] for url in files))
            self.releases[date]['version'] = version
        if not self.releases:
            raise ValueError("Package '{}' does not exist or haven't any release.".format(name))

        downloads = 0
        for release in sorted(self.releases):
            self.releases[release]['previous'] = downloads
            downloads += self.releases[release]['downloads']

    @property
    def total_downloads(self):
        """Return this package's total downloads (all versions combined)."""
        last = sorted(self.releases.keys())[-1]
        return self.releases[last]['downloads'] + self.releases[last]['previous']
