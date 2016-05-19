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
import decimal

import justbytes

from justoptions_gui import Config
from justoptions_gui import ChoiceSelector
from justoptions_gui import JustSelector
from justoptions_gui import MaybeSelector


class BaseConfig(Config):
    """
    Configuration gadget for base display.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbytes.Config.STRING_CONFIG.DISPLAY_CONFIG.base_config

    _FIELD_MAP = {
       "use_prefix": ("Display base prefix?", JustSelector(bool)),
       "use_subscript": ("Display base subscript?", JustSelector(bool))
    }


class StripConfig(Config):
    """
    Configuration gadget for stripping options.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbytes.Config.STRING_CONFIG.DISPLAY_CONFIG.strip_config

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

    CONFIG = justbytes.Config.STRING_CONFIG.DISPLAY_CONFIG.digits_config

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

    CONFIG = justbytes.Config.STRING_CONFIG.DISPLAY_CONFIG

    _FIELD_MAP = {
       "show_approx_str":
          ("Indicate if value is approximate?", JustSelector(bool))
    }


class ValueConfig(Config):
    """
    Configuration for choosing the value to display.
    """
    # pylint: disable=too-few-public-methods

    CONFIG = justbytes.Config.STRING_CONFIG.VALUE_CONFIG

    _FIELD_MAP = {
       "base": ("Base:", JustSelector(int)),
       "binary_units": ("Use IEC units?", JustSelector(bool)),
       "exact_value": ("Get exact value?", JustSelector(bool)),
       "max_places":
          (
             "Maximum number of digits right of radix:",
             MaybeSelector(JustSelector(int))
          ),
       "min_value":
          (
             "Bounding factor for non-fractional part:",
              JustSelector(decimal.Decimal)
          ),
       "rounding_method":
          (
             "Rounding method:",
             ChoiceSelector([
                (justbytes.ROUND_DOWN, "down"),
                (justbytes.ROUND_HALF_DOWN, "half down"),
                (justbytes.ROUND_HALF_UP, "half up"),
                (justbytes.ROUND_HALF_ZERO, "half 0"),
                (justbytes.ROUND_TO_ZERO, "to 0"),
                (justbytes.ROUND_UP, "up")
             ])
          ),
       "unit":
          (
             "Unit:",
             MaybeSelector(
                ChoiceSelector(
                   [(u, str(u)) for u in justbytes.UNITS()]
                )
             )
          )
    }
