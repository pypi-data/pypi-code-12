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
import Tkinter

import justbytes

from ._config import BaseConfig
from ._config import DigitsConfig
from ._config import MiscDisplayConfig
from ._config import StripConfig
from ._config import ValueConfig

from ._errors import GUIValueError


class RangeFrame(Tkinter.Frame):
    """
    Simple class to display a single Range value.
    """
    # pylint: disable=too-many-instance-attributes

    def _get_button_frame(self):
        """
        Make the bottom button frame.

        :returns: the enclosing frame for the buttons
        :rtype: Tkinter.Frame
        """
        button_frame = Tkinter.Frame(self)

        quit_button = \
           Tkinter.Button(button_frame, text="Quit", command=self.quit)
        quit_button.pack({"side": "right"})

        reset_button = \
           Tkinter.Button(button_frame, text="Reset", command=self.reset)
        reset_button.pack({"side": "right"})

        show_button = \
           Tkinter.Button(button_frame, text="Show", command=self.show)
        show_button.pack({"side": "right"})

        return button_frame

    def __init__(self, master=None):
        """
        Initializer.

        :param Tkinter.Widget master: the master
        """
        Tkinter.Frame.__init__(self, master)
        self.value = None
        self.pack()

        button_frame = self._get_button_frame()
        button_frame.pack({"side": "bottom"})

        self.DISPLAY_STR = Tkinter.StringVar()
        display_label = Tkinter.Label(
           self,
           textvariable=self.DISPLAY_STR,
           font=("Helvetica", 32)
        )
        display_label.pack({"side": "top"})

        self.ERROR_STR = Tkinter.StringVar()
        self.ERROR_STR.set("")
        error = Tkinter.Label(self, textvariable=self.ERROR_STR, fg="red")
        error.pack({"side": "top"})

        self.VALUE = ValueConfig(self, "Value")
        self.VALUE.widget.pack({"side": "left"})

        display = Tkinter.LabelFrame(self, text="Display")
        display.pack({"side": "left"})

        self.BASE = BaseConfig(display, "Base Options")
        self.BASE.widget.pack({"side": "top"})
        self.DIGITS = DigitsConfig(display, "Digits Options")
        self.DIGITS.widget.pack({"side": "top"})
        self.STRIP = StripConfig(display, "Strip Options")
        self.STRIP.widget.pack({"side": "top"})
        self.MISC = MiscDisplayConfig(display, "Miscellaneous Display Options")
        self.MISC.widget.pack({"side": "top"})

    def reset(self):
        """
        Reset to defaults and show.
        """
        self.VALUE.set(justbytes.ValueConfig())

        display_config = justbytes.DisplayConfig()
        self.BASE.set(display_config.base_config)
        self.DIGITS.set(display_config.digits_config)
        self.STRIP.set(display_config.strip_config)
        self.MISC.set(display_config)

        self.show()

    def show(self):
        """
        Show the resulting string.
        """
        try:
            base_config = justbytes.BaseConfig(**self.BASE.get())
            value_config = justbytes.ValueConfig(**self.VALUE.get())
            digits_config = justbytes.DigitsConfig(**self.DIGITS.get())
            strip_config = justbytes.StripConfig(**self.STRIP.get())
            display_config = justbytes.DisplayConfig(
               base_config=base_config,
               digits_config=digits_config,
               strip_config=strip_config,
               **self.MISC.get()
            )
            string_config = justbytes.StringConfig(
               value_config,
               display_config,
               justbytes.Config.STRING_CONFIG.DISPLAY_IMPL_CLASS
            )
        except (GUIValueError, justbytes.RangeError) as err:
            self.ERROR_STR.set(err)
            return

        try:
            self.DISPLAY_STR.set(
               self.value.getString(string_config)
            )
        except justbytes.RangeError as err:
            self.ERROR_STR.set(err)
            return

        self.ERROR_STR.set("")


def show(a_range):
    """
    Start a simple GUI to show display options for ``a_range``.

    :param Range a_range: the range to display
    """
    root = Tkinter.Tk()
    root.wm_title("Justbytes Range Viewer")
    frame = RangeFrame(master=root)
    frame.value = a_range
    frame.show()
    frame.mainloop()
    root.destroy()
