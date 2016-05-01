import sys

import enum

import numpy as np

from matplotlib.patches import Rectangle

import pyperclip


from mplapp.label import Label


#------------------------------------------------------------------------------
# for debugging

def dout_enabled(fmt, *args):
    print(fmt % args)


def dout_disabled(fmt, *args):
    pass

#~dout = dout_enabled
dout = dout_disabled

class Count(object):
    count = 0


class LineEdit(Label):
    """
    A text label.
    """

    def __init__(self, width, height, text, notify = None, **kwargs):

        self._str = text
        self._width = float(width)
        self._height = float(height)
        self._state = State.IDLE

        self._dbg_name = 'LE%d' % Count.count

        Count.count += 1

        # defaults
        ec = 'black'
        fc = 'white'
        color = 'black'
        ha = 'left'
        pad_left = 0.07 # inches
        highlight = [0.5859, 0.6406, 1.0]

        if 'ec' not in kwargs and 'edgecolor' not in kwargs:
            kwargs['ec'] = ec

        if 'fc' not in kwargs and 'facecolor' not in kwargs:
            kwargs['fc'] = fc

        if 'color' not in kwargs:
            kwargs['color'] = color

        if 'ha' not in kwargs and 'horizontalalignment' not in kwargs:
            kwargs['ha'] = ha

        if 'pad_left' in kwargs:
            pad_left = kwargs['pad_left']
            del kwargs['pad_left']

        if 'hl' in kwargs:
            highlight = kwargs['hl']
            del kwargs['hl']

        if 'highlight' in kwargs:
            highlight = kwargs['highlight']
            del kwargs['highlight']

        self._hl_color = highlight
        self._hl_x0 = None

        self._kwargs = kwargs

        self._pad_left = pad_left

        if notify and not callable(notify):
            raise ValueError('notify must be a callable function')

        self._notify = notify

        self._axes = None
        self._colors = ()

        self._cursor = None
        self._cursor_idx = None
        self._highlight = None


    def _render(self, fig, x, y):

        super(LineEdit, self)._render(fig, x, y)

        pos = list(self._text.get_position())

        pos[0] += self._pad_left

        self._text.set_position(pos)

        self.canvas().mpl_connect(
            'button_press_event', self._on_mouse_down)

        self.canvas().mpl_connect(
            'button_release_event', self._on_mouse_up)

        self.canvas().mpl_connect(
            'motion_notify_event', self._on_mouse_motion)

        self.canvas().mpl_connect(
            'key_press_event', self._on_key_press)

        self.canvas().mpl_connect(
            'key_release_event', self._on_key_release)


    def _render_cursor(self, x, units):
        """
        Determine where to place cursor
        """

        # render subtext elements to find nearest charactor position for
        # the cursor

        text_idx, xdata = _search_text(self._text, x, units)

        self._cursor_idx = text_idx

        # first time rending cursor?

        if self._cursor is None:
            color = self._text.get_color()
            self._cursor = self._axes.axvline(xdata, 0.1, 0.9, color = color)

        else:
            self._cursor.set_data([[xdata, xdata], [0.1, 0.9]])

        self._cursor.set_visible(True)

        if self._state == State.SELECTING:

            width = xdata - self._hl_x0
            self._highlight.set_width(width)


    def _change_state(self, new_state, **kwargs):

        if self._state == new_state:
            dout(
                "%s._change_state(%s): already in state %s, ignoring",
                self._dbg_name,
                new_state,
                self._state,
            )
            return

        dout(
            '%s._change_state(): state transition %s --> %s: kwargs=%s',
            self._dbg_name,
            self._state,
            new_state,
            repr(kwargs),
        )

#~        if new_state == self._state:
#~            raise RuntimeError("already in state %s" % self._state)

        if self._state == State.IDLE:

            if new_state == State.SELECTED:
                self._select_all()

            elif new_state == State.SELECTING:
                self._start_selecting(**kwargs)

            else:
                self._unhandled_state_transition(new_state)

        elif self._state == State.SELECTING:

            if new_state == State.TYPING:
                self._stop_selecting()
                if 'x_pixel' in kwargs:
                    self._render_cursor(kwargs['x_pixel'], 'pixel')

            elif new_state == State.SELECTED:

                if 'x_pixel' in kwargs:

                    dout("%s: kwargs = %s", self._dbg_name, kwargs)

                    self._render_cursor(kwargs['x_pixel'], 'pixel')

                # nothing selected?

                if self._highlight.get_visible() is False:
                    self._change_state(State.TYPING)
                    return

                else:
                    i0, i1 = self._get_selected_range()

                    if i0 == i1:
                        self._change_state(State.TYPING)
                        return

            elif new_state == State.IDLE:
                self._stop_selecting()
                key = kwargs.get('key', None)
                self._stop_typing(key)

            else:
                self._unhandled_state_transition(new_state)

        elif self._state == State.SELECTED:

            if new_state == State.TYPING:
                if 'key' in kwargs:
                    self._replace_selection(kwargs['key'])

                self._highlight.set_visible(False)

            elif new_state == State.SELECTING:
                self._stop_selecting()

            elif new_state == State.IDLE:
                self._stop_selecting()
                self._cursor.set_visible(False)

            else:
                self._unhandled_state_transition(new_state)

        elif self._state == State.TYPING:

            if new_state == State.SELECTING:
                self._start_selecting(**kwargs)

            elif new_state == State.SELECTED:
                pass

            elif new_state == State.IDLE:
                self._stop_typing()

            else:
                self._unhandled_state_transition(new_state)

        elif new_state == State.IDLE:
            self._stop_selecting()
            self._stop_typing('enter')

        else:
            self._unhandled_state_transition(new_state)

        #----------------------------------------------------------------------
        # change state and update canvas

        self._state = new_state

        self.canvas().draw()


    def _unhandled_state_transition(self, new_state):

        raise RuntimeError(
            '%s: unhandled state transition %s --> %s' % (
                self._dbg_name,
                self._state,
                new_state,
            )
        )


    def _replace_selection(self, new_text):

        if self._highlight.get_visible():

            i0, i1 = self._get_selected_range()

        else:
            i0 = self._cursor_idx
            i1 = i0

        s = self.text()

        s = s[0:i0] + new_text + s[i1:]

        self.text(s)

        self._render_cursor(i0 + len(new_text), 'index')


    def _stop_typing(self, key = None):

        dout('%s._stop_typing(%s)', self._dbg_name, repr(key))

        if self._cursor:
            self._cursor.set_visible(False)
            self.canvas().draw()

        if self._notify and key == 'enter':
            self._notify(self.text())

#~            # restore default keymap

#~            for key in self._rc_keys_disabled:
#~                rcParams[key] = self._rc_keys_disabled[key]


    def _start_selecting(self, x_pixel = None, x0 = None, width = 0):

        dout('%s._start_selecting()', self._dbg_name)

        if x_pixel:

            txt_idx, x = _search_text(self._text, x_pixel, 'pixel')

            self._hl_x0 = x

            if self._cursor_idx is None:
                self._render_cursor(x_pixel, 'pixel')

        elif x0:
            self._hl_x0 = x0

        else:
            x = self._cursor.get_data()[0]
            self._hl_x0 = x[0]

        if self._highlight is None:

            pos = self._hl_x0, 0

            r = Rectangle(pos, width, 1, ec = self._hl_color, fc = self._hl_color)

            self._highlight = r

            self._axes.add_patch(r)

        else:

            self._highlight.set_x(self._hl_x0)
            self._highlight.set_width(width)
            self._highlight.set_visible(True)

        self.canvas().draw()


    def _stop_selecting(self):

        if self._highlight:
            self._highlight.set_visible(False)


    def _select_all(self):

        n_chars = len(self.text())

        _, x0 = _search_text(self._text, 0, 'index')
        _, x1 = _search_text(self._text, n_chars, 'index')

        self._hl_x0 = x0
        width = x1 - x0

        if self._highlight is None:

            pos = self._hl_x0, 0

            r = Rectangle(pos, width, 1, ec = self._hl_color, fc = self._hl_color)

            self._highlight = r

            self._axes.add_patch(r)

        else:

            self._highlight.set_x(self._hl_x0)
            self._highlight.set_width(width)
            self._highlight.set_visible(True)

        self._render_cursor(n_chars, 'index')


    def _on_mouse_down(self, event):
        """
        Currently, click on a line edit, will dispatch an event to all widgets
        with 'button_press_event' callbacks.

        This this callback is called whenever a wiget is clicked.

        For a line edit, if the click didn't occur inside it's axes, transition
        to IDLE, else, transition to SELECTING/SELECTED.
        """

        x, y = event.xdata, event.ydata

        if event.inaxes != self._axes or None in [x, y]:
            if self._state != State.IDLE:
                self._change_state(State.IDLE)
            return

        dout('%s._on_mouse_down()', self._dbg_name)

        if event.dblclick:
            dout('    %s: double click!', self._dbg_name)
            self._select_all()
            self._change_state(State.SELECTED)

        else:
            dout('    %s: normal click', self._dbg_name)
            self._change_state(State.SELECTING, x_pixel = event.x)


    def _on_mouse_up(self, event):

        if event.inaxes != self._axes or None in [event.xdata, event.ydata]:
            return

        self._change_state(State.SELECTED, x_pixel = event.x)


    def _on_mouse_motion(self, event):

        x, y = event.xdata, event.ydata

        if event.inaxes != self._axes or None in [x, y]:
            return

        if self._state != State.SELECTING:
            return

        width = x - self._hl_x0
        self._highlight.set_width(width)
        self.canvas().draw()


    def _on_key_press(self, event):

        if self._state == State.IDLE:
            return

        key = event.key

        dout(
            "%s._on_key_press(%s): self._state = %s",
            self._dbg_name,
            key,
            self._state,
        )

        if key is None:  # TAB key
            return

        # normal keys are length 1

        if len(key) == 1:

            if self._state in [State.SELECTING, State.SELECTED, State.TYPING]:

                dout("    %s: inserting char '%s'", self._dbg_name, key)

                self._replace_selection(key)

                if self._state != State.TYPING:
                    self._change_state(State.TYPING)

                else:
                    self.canvas().draw()

            if self._state != State.TYPING:
                self._change_state(State.TYPING)

        elif key == 'backspace':

            if self._cursor_idx == 0:
                return

            text_idx, xdata = _search_text(
                self._text, self._cursor_idx, 'index')

            s = self.text()

            s = s[0:text_idx-1] + s[text_idx:]

            self.text(s)

            self._render_cursor(self._cursor_idx - 1, 'index')

        elif key == 'delete':
            self._do_delete()
            self._change_state(State.TYPING)

        elif key == 'left':

            if self._cursor_idx == 0:
                return

            self._render_cursor(self._cursor_idx - 1, 'index')

            if self._state == State.SELECTED:
                self._change_state(State.TYPING)

            else:
                self.canvas().draw()

        elif key == 'right':

            N = len(self.text())

            if self._cursor_idx == N:
                return

            self._render_cursor(self._cursor_idx + 1, 'index')

            if self._state == State.SELECTED:
                self._change_state(State.TYPING)

            else:
                self.canvas().draw()

        elif key == 'home':

            if self._state != State.SELECTING:
                self._stop_selecting()

            if self._cursor_idx == 0:
                return

            self._cursor_idx = 0

            self._render_cursor(self._cursor_idx, 'index')
            self.canvas().draw()

        elif key == 'end':

            if self._state != State.SELECTING:
                self._stop_selecting()

            N = len(self.text())

            if self._cursor_idx == N:
                return

            self._cursor_idx = N

            self._render_cursor(self._cursor_idx, 'index')
            self.canvas().draw()

        elif key == 'enter':
            self._stop_typing(key)

        elif key == 'escape':
            self._stop_selecting()
            self._stop_typing(key)
            self._state = State.IDLE

        elif key == 'shift':
            if self._state not in [State.SELECTING, State.SELECTED]:
                self._change_state(State.SELECTING)

        elif key in ['ctrl+c', 'ctrl+x']:

            start, end = self._highlight.get_window_extent().get_points()

            x0, x1 = start[0], end[0]

            i0, _ = _search_text(self._text, x0, 'pixel')
            i1, _ = _search_text(self._text, x1, 'pixel')

            delta = i1 - i0

            if delta == 0:
                return

            s = self.text()

            pyperclip.copy(s[i0:i1])

            if key == 'ctrl+x':
                self._do_delete()


        elif key == 'ctrl+v':

            temp = pyperclip.paste()

            i0, i1 = self._get_selected_range()

            s = str(self.text())

            s = s[0:i0] + temp + s[i1:]

            self.text(s)

            self._cursor_idx = i0 + len(temp)

            self._render_cursor(self._cursor_idx, 'index')

            self._stop_selecting()

        elif key == 'ctrl+a':
            self._select_all()
            self._change_state(State.SELECTED)

        elif key == 'ctrl':
            pass

        else:
            dout(
                "%s: unhandled key while in state %s: = %s",
                self._dbg_name,
                self._state,
                repr(key),
            )


    def _on_key_release(self, event):

        key = event.key

        dout(
            '%s._on_key_release(%s): state = %s',
            self._dbg_name,
            repr(key),
            self._state,
        )

        if key == 'shift' and self._state == State.SELECTING:

            self._change_state(State.SELECTED)


    def _get_selected_range(self):

        assert self._highlight.get_visible()

        start, end = self._highlight.get_window_extent().get_points()

        x0, x1 = start[0], end[0]

        i0, _ = _search_text(self._text, x0, 'pixel')
        i1, _ = _search_text(self._text, x1, 'pixel')

        return i0, i1


    def _do_delete(self):
        """
        called by pressing the delete key or ctrl+x
        """

        N = len(self.text())

        s = self.text()

        i0, i1 = self._get_selected_range()

        if self._cursor_idx > i0:
            self._cursor_idx = i0

        if i1 > i0:
            s = s[0:i0] + s[i1:]

        elif i0 == i1:
            s = s[0:i0] + s[i0+1:]

        else:
            s = s[0:i0] + s[i1:]

        self.text(s)

        self._render_cursor(self._cursor_idx, 'index')


#------------------------------------------------------------------------------
# render text element and inspect the bounding box

def _search_text(text, x, units):

#~    dout("_search_text(x=%f, units=%s)", x, units)

    char_pos = np.array(_get_text_positions(text))

    if units == 'pixel':

#~        dout("    subtracting float from np.array")

        dist = np.abs(char_pos - float(x))

        x_idx = np.round(dist).argmin()

    elif units == 'index':
        x_idx = x

#~        dout("    len(char_pos) = %d", len(char_pos))
#~        dout("    x_idx = %d", x_idx)

    else:
        raise ValueError('unknown unit %s' % repr(units))

    assert x_idx >= 0
    assert x_idx <= len(char_pos)

#~    dout("    indexing into np.array")

    x_pixel = char_pos[x_idx]

#~    dout("    x_pixel = %f", x_pixel)

    # now convert pixels to data units

    pixel_to_data_transform = text.axes.transData.inverted()

    xdata = pixel_to_data_transform.transform((x_pixel, 0))[0]

#~    dout("    returning xdata=%f", xdata)

    return x_idx, xdata


def _get_text_positions(text):
    '''
    For each character in the text object, return a list pixel values for
    the start of each character.

    Note, this returns a list that is len(text) + 1, so that the end of the
    last character can be determined.
    '''

    orig = text.get_text()

    #--------------------------------------------------------------------------
    # the backend render ignores leading trailing whitespace, so lets directly
    # measure the width of a space

    text.set_text('##')

    bb = text.get_window_extent()

    width0 = bb.width

    text.set_text('# #')

    bb = text.get_window_extent()

    width1 = bb.width

    space_width = width1 - width0

    #--------------------------------------------------------------------------
    # measure the position of each character

    s = str(orig)

    N = len(s)

    x_positions = [bb.x0]

    for i in range(1, N + 1):

        txt = s[0:i]

        text.set_text(txt)

        bb = text.get_window_extent()

        x = bb.x0 + bb.width

        # adjust for spaces
        if txt[0] == ' ':
            x += space_width

        if i > 0 and txt[-1] == ' ':
            x += space_width

        x_positions.append(x)

    # restore text

    text.set_text(orig)

    return x_positions


#------------------------------------------------------------------------------
# Support classes / functions

class State(enum.Enum):

    IDLE = 0
    TYPING = 1
    SELECTING = 2
    SELECTED = 3
