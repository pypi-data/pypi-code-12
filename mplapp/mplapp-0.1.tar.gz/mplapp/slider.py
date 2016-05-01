import matplotlib
from matplotlib.patches import Rectangle


from mplapp.base import Base


class Slider(Base):
    """
    A slider that responds to mouse clicks and motion
    """

    IDLE = 0
    SLIDING = 1

    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, width, height, **kwargs):

        self._notify = kwargs.get('notify', None)
        self._vinit = kwargs.get('vinit', 0.5)
        self._vmax = kwargs.get('vmax', 1.0)
        self._vmin = kwargs.get('vmin', 0.0)
        self._vrange = self._vmax - self._vmin

        if width > height:
            self._orientation = self.HORIZONTAL
        else:
            self._orientation = self.VERTICAL

        self._width = float(width)
        self._height = float(height)

        fg = 'blue'
        bg = 'white'
        ec = 'black'

        if 'fg' in kwargs:
            fg = kwargs['fg']

        if 'foreground' in kwargs:
            fg = kwargs['foreground']

        if 'bg' in kwargs:
            bg = kwargs['bg']

        if 'background' in kwargs:
            bg = kwargs['background']

        if 'ec' in kwargs:
            ec = kwargs['ec']

        if 'edgecolor'in kwargs:
            ec = kwargs['edgecolor']

        self._colors = dict(fg = fg, bg = bg, ec = ec)

        self._axes = None

        self._state = self.IDLE


    def axes(self):
        if self._axes:
            return self._axes
        raise RuntimeError('This widget has not been rendered yet')


    def canvas(self):
        if self._axes:
            return self._axes.figure.canvas
        raise RuntimeError('This widget has not been rendered yet')


    def size(self):
        return self._width, self._height


    def value(self, new_value = None):

        if new_value is None:
            if self._orientation == self.HORIZONTAL:
                return self._rect.get_width()

            else:
                return self._rect.get_height()

        else:

            if self._orientation == self.HORIZONTAL:
                self._rect.set_width(new_value)

            else:
                self._rect.set_height(new_value)

            self.canvas().draw_idle()

            if self._notify:
                self._notify(new_value)


    def _render(self, fig, x, y):

        # convert size to percent of figure

        W, H = fig.get_size_inches()

        x /= W
        y /= H

        w, h = self.size()

        w /= W
        h /= H

        ax = fig.add_axes([x, y, w, h], xticks=[], yticks=[])

        # apply colors

        bg = self._colors['bg']
        ec = self._colors['ec']
        fg = self._colors['fg']

        # background color

        ax.set_axis_bgcolor(bg)

        # edge color

        for side in ['bottom', 'top', 'left', 'right']:
            ax.spines[side].set_color(ec)

        # a rectangle representing the slider

        if self._orientation == self.HORIZONTAL:

            xy = (0,0)
            width = self._vinit
            height = 1.0

            ax.set_xlim([self._vmin, self._vmax])
            ax.set_ylim([0, 1])

        else:

            xy = (0,0)
            width = 1.0
            height = self._vinit

            ax.set_xlim([0, 1])
            ax.set_ylim([self._vmin, self._vmax])

        self._rect = Rectangle(xy, width, height, ec = fg, fc = fg)

        ax.add_patch(self._rect)

        self._axes = ax

        self.canvas().mpl_connect(
            'button_press_event', self._on_mouse_click)

        self.canvas().mpl_connect(
            'button_release_event', self._on_mouse_release)

        self._cid_motion = self.canvas().mpl_connect(
            'motion_notify_event', self._on_mouse_motion)


    def _on_mouse_click(self, event):

        if event.inaxes != self._axes:
            return

        if self._orientation == self.HORIZONTAL:
            self.value(event.xdata)

        else:
            self.value(event.ydata)

        self._state = self.SLIDING


    def _on_mouse_release(self, event):
        if event.inaxes != self._axes:
            return

        self._state = self.IDLE


    def _on_mouse_motion(self, event):

        if event.inaxes != self._axes:
            return

        if self._state != self.SLIDING:
            return

        if self._orientation == self.HORIZONTAL:
            self.value(event.xdata)

        else:
            self.value(event.ydata)
