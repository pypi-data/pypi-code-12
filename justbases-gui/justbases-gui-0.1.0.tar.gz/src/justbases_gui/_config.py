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
Highest level code for module.
"""
import justbases

from justoptions_gui import Config
from justoptions_gui import ChoiceSelector
from justoptions_gui import JustSelector
from justoptions_gui import MaybeSelector


class BaseConfig(Config):
    """
    Configuration gadget for base display.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbases.BasesConfig.DISPLAY_CONFIG.base_config

    _FIELD_MAP = {
       "use_prefix": ("Display base prefix?", JustSelector(bool)),
       "use_subscript": ("Display base subscript?", JustSelector(bool))
    }


class StripConfig(Config):
    """
    Configuration gadget for stripping options.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbases.BasesConfig.DISPLAY_CONFIG.strip_config

    _FIELD_MAP = {
       "strip": ("Strip all trailing zeros?", JustSelector(bool)),
       "strip_exact": ("Strip trailing zeros if exact?", JustSelector(bool)),
       "strip_whole":
          (
             "Strip trailing zeros if exact whole number?",
             JustSelector(bool)
          )
    }


class DigitsConfig(Config):
    """
    Configuration for property of digits.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbases.BasesConfig.DISPLAY_CONFIG.digits_config

    _FIELD_MAP = {
       "separator": ("Separator:", JustSelector(str)),
       "use_caps": ("Use capital letters?", JustSelector(bool)),
       "use_letters": ("Use letters for digits?", JustSelector(bool))
    }


class MiscDisplayConfig(Config):
    """
    Miscellaneous display options.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbases.BasesConfig.DISPLAY_CONFIG

    _FIELD_MAP = {
       "show_approx_str":
          ("Indicate if value is approximate?", JustSelector(bool))
    }


class ValueFields(object):
    """
    Class to hold the fields contained by the value widget.
    """
    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        base=10,
        precision=2,
        rounding_method=justbases.RoundingMethods.ROUND_HALF_ZERO
    ):
        """
        Initializers.

        :param int base: the base
        :param int precision: the precision
        :param rounding_method: the rounding method
        :type rounding_method: one of RoundingMethods.METHODS()
        """
        self.base = base
        self.precision = precision
        self.rounding_method = rounding_method


class ValueConfig(Config):
    """
    Configuration for choosing the value to display.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = ValueFields()

    _FIELD_MAP = {
       "base": ("Base:", JustSelector(int)),
       "precision":
          (
             "Maximum number of digits right of radix:",
             MaybeSelector(JustSelector(int))
          ),
       "rounding_method":
          (
             "Rounding method:",
             ChoiceSelector([
                (justbases.RoundingMethods.ROUND_DOWN, "down"),
                (justbases.RoundingMethods.ROUND_HALF_DOWN, "half down"),
                (justbases.RoundingMethods.ROUND_HALF_UP, "half up"),
                (justbases.RoundingMethods.ROUND_HALF_ZERO, "half 0"),
                (justbases.RoundingMethods.ROUND_TO_ZERO, "to 0"),
                (justbases.RoundingMethods.ROUND_UP, "up")
             ])
          )
    }
