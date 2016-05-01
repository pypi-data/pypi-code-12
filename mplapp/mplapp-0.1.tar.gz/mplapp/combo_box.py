import enum

import numpy as np

from matplotlib import rcParams
from matplotlib.patches import Rectangle
from matplotlib.patches import Polygon

import pyperclip


from mplapp.line_edit import LineEdit


_DEV = True


class ComboBox(LineEdit):
    """
    A ComboxBox, upon clicking button, drops down a list of items to choose.

    Items can be edited also.
    """


    def __init__(
            self,
            width,
            height,
            text_list,
            edit_notify = None,
            selection_notify = None,
            **kwargs
        ):

        if len(text_list) > 0:
            text = text_list[0]
        else:
            text = ''

        super(ComboBox,self).__init__(
            width, height, text, self._on_edit_notify, **kwargs)

        self._text_list = text_list

        self._edit_notify = edit_notify
        self._selection_notify = selection_notify

        if edit_notify and not callable(edit_notify):
            raise RuntimeError('edit_notify must be a callable function')

        if selection_notify and not callable(selection_notify):
            raise RuntimeError('selection_notify must be a callable function')

        #---------------------------------------------------------------------
        # additional items
        #
        # selection axes for showing the possible selections
        # a rectangle to highlight the selection row
        # a button to show the selection drop down

        self._select_axes = None
        self._select_highlight = None # just a rectangle
        self._select_posx = None
        self._select_entries = []

        self._cb_state = ComboState.IDLE

        self._n_lines = 5

        self._mouse_motion_cid = None

        self._ignore_edit_notify = False


    def _render(self, fig, x, y):

        super(ComboBox, self)._render(fig, x, y)

        self._render_dropdown_button(fig)
        self._render_dropdown_axis(fig, x, y)


    def _render_dropdown_axis(self, fig, x, y):

        W, H = fig.get_size_inches()

        h = self._n_lines * self._height

        y -= h

        x /= W
        y /= H

        # create the other gui assets but keep them hidden

        # selection axes, same width, by 10 times in height

        w = self._width / W
        h /= H

        ax = fig.add_axes([x, y, w, h], xticks=[], yticks=[])

        ax.set_xlim([0, self._width])
        ax.set_ylim([0, self._n_lines * self._height])

        ax.set_axis_bgcolor('white')

        ax.set_visible(False)

        ax.set_zorder(1000)

        self._select_axes = ax


    def _render_dropdown_button(self, fig):

        w, h = 0.25, 0.125

        hw = w / 2.0
        hh = h / 2.0

        x = self._width - w - 0.02
        y = (self._height - h) / 2.0

        self._select_posx = x + hw

        # Three point polygon:
        #
        #  2 O-----O 3
        #     \   /
        #      \ /
        #       O
        #       1
        #

        points = [
            [ x + hw, y    ],
            [ x,      y + h],
            [ x + w,  y + h],
        ]

        points = np.array(points)

        patch = Polygon(points, closed = True, ec = 'black', fc = 'black')

        self._axes.add_patch(patch)


    def _cb_change_state(self, new_state):

        if self._cb_state == new_state:
            raise RuntimeError("Already in state %s" % new_state)

        if self._cb_state == ComboState.IDLE:

            if new_state == ComboState.DROP_SELECT:
                self._select_axes.set_visible(True)

                x = self._pad_left
                y = ((self._n_lines - 1) * self._height)

                #--------------------------------------------------------------
                # create highlight

                if self._select_highlight is None:

                    self._select_highlight = Rectangle(
                        (0,y - self._height / 2.0),
                        self._width,
                        self._height,
                        ec = self._hl_color,
                        fc = self._hl_color
                    )

                    self._select_axes.add_patch(self._select_highlight)

                else:
                    self._select_highlight.set_visible(True)

                # delete existing text objects

                for t in self._select_entries:
                    t.remove()
                    del t

                self._select_entries = []

                for t in self._text_list:

                    txt = self._select_axes.text(
                        x,y,t, ha = 'left', va = 'center')

                    y -= self._height

                    self._select_entries.append(txt)

                self._mouse_motion_cid = self._select_axes.figure.canvas.mpl_connect(
                    'motion_notify_event', self._on_mouse_motion
                )

                self.canvas().draw()

            else: self._unhandled_state(new_state)

        elif self._cb_state == ComboState.DROP_SELECT:

            if new_state == ComboState.IDLE:
                self._select_axes.set_visible(False)
                self.canvas().draw()

            else: self._unhandled_state(new_state)

        else: self._unhandled_state(new_state)

        self._cb_state = new_state


    def _unhandled_state(self, new_state):
        if _DEV:
            print("unhandled %s --> %s" % (self._cb_state, new_state))


    def _on_mouse_down(self, event):

        if event.inaxes not in [self._axes, self._select_axes]:
            self._ignore_edit_notify = True
            if self._cb_state != ComboState.IDLE:
                self._cb_change_state(ComboState.IDLE)
            super(ComboBox, self)._on_mouse_down(event)
            return

        x, y = event.xdata, event.ydata

        if x is None or y is None:
            super(ComboBox, self)._on_mouse_down(event)
            return

        if self._cb_state == ComboState.IDLE:

            cx = self._select_posx

            d = np.sqrt( (x - cx) ** 2 )

            if d <= 0.16:
                self._cb_change_state(ComboState.DROP_SELECT)

            else:
                super(ComboBox, self)._on_mouse_down(event)

        elif self._cb_state == ComboState.DROP_SELECT:

            y = self._select_highlight.get_y()

            idx = self._find_text_entry(y)

            selection = self._text_list[idx]

            self._ignore_edit_notify = True

            self.text(selection)

            if self._selection_notify:
                self._selection_notify(idx, selection)

            self._cb_change_state(ComboState.IDLE)

        elif _DEV:
            print("on_mouse_down(): unhandled %s" % self._cb_state)


    def _on_mouse_motion(self, event):

        if event.inaxes != self._select_axes:
            return

        x, y = event.xdata, event.ydata

        if x is None or y is None:
            return

        if self._cb_state == ComboState.DROP_SELECT:

            idx = self._find_text_entry(y)

            _, y = self._select_entries[idx].get_position()

            self._select_highlight.set_y(y - self._height / 2.0)

            self.canvas().draw()


    def _on_key_press(self, event):

        if event.key == 'escape' and self._cb_state == ComboState.DROP_SELECT:
            self._cb_change_state(ComboState.IDLE)

        self._ignore_edit_notify = False

        super(ComboBox, self)._on_key_press(event)


    def _find_text_entry(self, y):

         # find nearest text

        dist = []

        for txt in self._select_entries:

            _, ydata = txt.get_position()

            d = np.abs(ydata - y)

            dist.append(d)

        return np.argmin(dist)


    def _on_edit_notify(self, text):

        if self._ignore_edit_notify:
            self._ignore_edit_notify = False
            return

        # add to the list

        self._text_list.append(text)

        if self._edit_notify:
            self._edit_notify(text)



#------------------------------------------------------------------------------
# Support classes

class ComboState(enum.Enum):

    IDLE = 0
    DROP_SELECT = 1

