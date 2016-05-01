# Python
import colorsys
import time

from matplotlib.colors import ColorConverter

from mplapp.label import Label


class Button(Label):
    """
    A push button.
    """

    def __init__(self, width, height, text, callback = None, **kwargs):

        if callback and not callable(callback):
            raise ValueError("callback isn't callable!")

        self._callback = callback

        ec = 'black'

        if 'ec' not in kwargs and 'edgecolor' not in kwargs:
            kwargs['ec'] = ec

        super(Button, self).__init__(width, height, text, **kwargs)

        self._cid = None


    def is_enabled(self):
        return self._cid is not None


    def enable(self):

        if self._cid: # already enabled?
            return

        # set enabled colors

        ec, fc, text_color = self._colors

        ax = self._axes

        ax.set_axis_bgcolor(fc)

        for side in ['bottom', 'top', 'left', 'right']:
            ax.spines[side].set_color(ec)

        self._text.set_color(text_color)

        self._axes.figure.canvas.draw()

        self._cid = self._axes.figure.canvas.mpl_connect(
            'button_press_event', self._blink_on_click)


    def disable(self):

        if self._cid is None: # already disabled?
            return

        self._axes.figure.canvas.mpl_disconnect(self._cid)
        self._cid = None

        # set disabled colors

        ax = self._axes

        grey65 = [1.0 - 0.65] * 3
        grey45 = [1.0 - 0.45] * 3
        grey25 = [1.0 - 0.20] * 3

        ax.set_axis_bgcolor(grey25)

        for side in ['bottom', 'top', 'left', 'right']:
            ax.spines[side].set_color(grey45)

        self._text.set_color(grey65)

        self._axes.figure.canvas.draw()


    def _render(self, fig, x, y):
        super(Button, self)._render(fig, x, y)

        self._cid = self._axes.figure.canvas.mpl_connect(
            'button_press_event',
            self._blink_on_click
        )


    def _blink_on_click(self, event):
        """
        'blink' the axis color to give visual feedback the button has been
        pressed.

        Reference: http://stackoverflow.com/a/1165145/562106

        """

        if event.inaxes != self._axes:
            return

        orig_color = self._axes.get_axis_bgcolor()

        r,g,b = ColorConverter().to_rgb(orig_color)

        cmax = max([r,g,b])
        cmin = min([r,g,b])

        # gray?
        if abs(cmax - cmin) < 5:

            if cmax > 0.5:
                r,g,b = 0.10,0.10,0.10
            else:
                r,g,b = 0.90,0.90,0.90

        h,l,s = colorsys.rgb_to_hls(r,g,b)

        # invert hue
        h = 360.0 - h

        new_color = colorsys.hls_to_rgb(h,l,s)

        self._axes.set_axis_bgcolor(new_color)
        self._axes.figure.canvas.draw()

        time.sleep(0.05)

        self._axes.set_axis_bgcolor(orig_color)
        self._axes.figure.canvas.draw()

        if self._callback:
            self._callback(event)
