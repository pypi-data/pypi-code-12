# -*- coding: utf-8 -*-
#
# PyParadox is a nix launcher for Paradox titles.
# Copyright (C) 2014  Carmen Bianca Bakker <carmenbbakker@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import logging
import json

import appdirs

from .core import GAMES

DEFAULT_CONFIG_DIR = appdirs.user_config_dir("PyParadox")

_logger = logging.getLogger(__name__)


def default_values(game):
    """Create and return a dictionary containing the default configuration
    values for each supported platform (Windows/OS X/Linux).

    :param str game: Shorthand version of the game (i.e., ck2, eu4, stel).
    :return: Default configuration values for ``mods``, ``excluded_dlcs``,
             ``binary_path`` and ``mod_path``.
    :rtype: dict
    """
    mods = []
    excluded_dlcs = []

    full_game = GAMES[game]

    # Windows
    if sys.platform.startswith("win"):
        binary_path = os.path.join(os.environ["ProgramFiles(x86)"],
                                   "Steam",
                                   "SteamApps",
                                   "common",
                                   full_game,
                                   "{}.exe".format(game))
        mod_path = os.path.join(os.path.expanduser("~"),
                                "Documents",
                                "Paradox Interactive",
                                full_game,
                                "mod")
    # OS X
    elif sys.platform == 'darwin':
        binary_path = os.path.join(appdirs.user_data_dir("Steam"),
                                   "steamapps",
                                   "common",
                                   full_game,
                                   "{}.app".format(game))
        mod_path = os.path.join(os.path.expanduser("~"),
                                "Documents",
                                "Paradox Interactive",
                                full_game,
                                "mod")
    # Linux
    else:
        binary_path = os.path.join(os.path.expanduser("~"),
                                   ".steam",
                                   "root",
                                   "steamapps",
                                   "common",
                                   full_game,
                                   game)
        mod_path = os.path.join(os.path.expanduser("~"),
                                ".paradoxinteractive",
                                full_game,
                                "mod")

    return {
        "game": game,
        "mods": mods,
        "excluded_dlcs": excluded_dlcs,
        "binary_path": binary_path,
        "mod_path": mod_path
    }


class JsonBackend:
    """Backend that implements an interface for reading and writing a
    :class:`Config` to a file, using the json format.
    """

    @staticmethod
    def read(stream):
        """Gather json data from the stream and return a dictionary of the
        gathered data.

        :param stream: Stream that contains json data.
        :type stream: file-like object
        :return: Data gathered from *stream*.
        :rtype: dict
        """
        return json.load(stream)

    @staticmethod
    def write(data, stream):
        """Write the data to a stream in a json format.

        :param dict data: Serialisable data.
        :param stream: Writeable stream.
        :type stream: file-like object
        """
        json.dump(data, stream, indent=4, sort_keys=True)


class Config(dict):
    """Simple dictionary with the added ability to read and write to file
    streams using (mostly) any format.
    """

    def __init__(self, *args, **kwargs):
        """Constructor for :class:`dict`.

        :keyword backend: Object with *read* and *write* properties.
        """

        self.backend = kwargs.pop("backend", JsonBackend)
        super().__init__(*args, **kwargs)

    @staticmethod
    def build_config(stream_or_file, default=None, backend=JsonBackend):
        """Factory method for :class:`Config`.

        Accepts a stream or file as  argument, from which the contents will be
        forwarded to the constructor of the *Config* object.

        If *default* is provided, the contents of the *Config* object will be
        set to the provided default values if the file or stream is invalid.

        :param stream_or_file: Holds the contents that the *Config* object will
                               be initialised with.
        :type stream_or_file: file-like object or str
        :keyword dict default: Default values if reading from *stream_or_file*
                               was unsuccessful.
        :keyword backend: Backend that will be used to read *stream_or_file*,
                          and the *Config* object will be initialised with.
        :return: *Config* object.
        :rtype: :class:`Config`
        """
        try:
            stream = open(stream_or_file)
        except TypeError:
            stream = stream_or_file
        except FileNotFoundError:
            _logger.warning("{} not found, using default".format(
                stream_or_file))
            stream = None

        if stream:
            data = backend.read(stream)
            stream.close()
        else:
            data = default if default is not None else dict()

        return Config(data, backend=backend)

    def load(self, stream, override=True, suppress_merge=False):
        """Load the contents of *stream* to self.

        *override* determines whether the contents of *stream* should be able
        to override self.  If *override* is :const:`False` and a key is being
        overridden, it will raise an :class:`AttributeError`.

        *suppress_merge* is only relevant if *override* is :const:`False`.  It
        explicitly silences errors that arise if a key already exists in the
        dictionary.

        :param stream: Stream that contains a valid format for the backend to
                       read.
        :type stream: file-like object
        :keyword bool override: Whether keys from *stream* should be able to
                                override self.
        :keyword bool suppress_merge: Whether errors arising from conflicting
                                      keys should be silenced.
        :raise AttributeError: If a key from *stream* conflicts with self.
        """
        data = self.backend.read(stream)
        if override:
            self.update(data)
        else:
            for key, value in data.items():
                if key in self:
                    if not suppress_merge:
                        raise AttributeError("key '{}' already exists".format(
                            key))
                else:
                    self[key] = value

    def save(self, stream):
        """Save self to *stream*, using the backend format.

        :param stream: Writeable stream.
        :type stream: file-like object
        """
        _logger.info("saving config to {}".format(stream.name))
        self.backend.write(self, stream)


class FileConfig(Config):
    """Sub-class of :class:`Config` that internally stores a file path that
    it uses every time a ``load()`` or ``save()`` method is called.
    """

    def __init__(self, path, *args, **kwargs):
        """Constructor for :class:`FileConfig`.

        :param str path: Path where the configuration file can be found.
        """
        super().__init__(*args, **kwargs)
        self.path = path

    @staticmethod
    def build_config(path, default=None, backend=JsonBackend):
        """Factory method for :class:`FileConfig`. Most functionality exists in
        :meth:`Config.build_config`.

        :param str path: Path where the configuration file can be found.
        :param dict default: Default values if reading from *stream_or_file*
                             was unsuccessful.
        :param backend: Backend that will be used to read *stream_or_file*,
                        and the *Config* object will be initialised with.
        """
        config = Config.build_config(path, default=default, backend=backend)

        return FileConfig(path, dict(config.items()), backend=backend)

    def load(self, override=True, suppress_merge=True):
        """Load the contents of *path* onto self. Most logic contained within
        :meth:`Config.load``.

        :keyword bool override: Whether keys from *path* should be able to
                                override self.
        :keyword bool suppress_merge: Whether errors arising from conflicting
                                      keys should be silenced.
        :raise AttributeError: If a key from *path* conflicts with self.
        """
        with open(self.path):
            super().load(self.path, override=override,
                         suppress_merge=suppress_merge)

    def save(self):
        """Save self to *path*, using the backend format."""
        _mkdir_p(os.path.dirname(self.path))

        with open(self.path, "w") as fp:
            super().save(fp)


def _mkdir_p(directory):
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass
