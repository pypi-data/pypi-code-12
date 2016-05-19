# Copyright (C) 2016 Anne Mulhern
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# Anne Mulhern <mulhern@cs.wisc.edu>

"""
Abstract Config class.

To make use of the facilities of this package, it is necessary to
implement subclasses of the Config class by defining the abstract properties
CONFIG and _FIELD_MAP.

CONFIG is a class with an initializer which takes keyword arguments.
_FIELD_MAP maps the keywords to a pair of a string and a Selector.
The string is a label for the option, the selector describes how
the value for the option is obtained from the user.

"""
import abc
import decimal
import Tkinter

from six import add_metaclass

from ._errors import GUIValueError

from ._gadgets import Entry


@add_metaclass(abc.ABCMeta)
class Config(object):
    """ Top level class for configuration gadgets. """
    # pylint: disable=too-few-public-methods

    CONFIG = abc.abstractproperty(doc="associated configuration")
    _FIELD_MAP = abc.abstractproperty(doc="map from field names to gadgets")

    def get(self):
        """
        Get a dictionary of values associated with this gadget.

        :returns: a dictionary of value
        :rtype: dict of str * object
        """
        kwargs = dict()

        for config_attr in sorted(self._FIELD_MAP.keys()):
            try:
                kwargs[config_attr] = self._field_vars[config_attr].get()
            except (ValueError, decimal.InvalidOperation):
                raise GUIValueError(
                   "value for \"%s\" could not be converted" % config_attr
                )

        return kwargs

    def set(self, config):
        """
        Set the members according to ``config``.

        :param config: a configuration
        :type config: a justbytes configuration
        """
        for config_attr in self._FIELD_MAP.keys():
            self._field_vars[config_attr].set(getattr(config, config_attr))

    widget = property(lambda s: s.VALUE, doc="top level widget")

    def __init__(self, master, label_str):
        """
        Initializer.

        :param Tkinter.Widget master: the master widget
        :param str label_str: how to label the top-level widget
        """
        self._field_vars = dict()

        self.VALUE = Tkinter.LabelFrame(master, text=label_str)

        for config_attr in sorted(self._FIELD_MAP.keys()):
            (label_text, widget_selector) = self._FIELD_MAP[config_attr]
            entry = Entry.getWidget(
               self.VALUE,
               widget_selector,
               getattr(self.CONFIG, config_attr),
               label_text
            )
            entry.widget.pack({"side": "top"})
            self._field_vars[config_attr] = entry
