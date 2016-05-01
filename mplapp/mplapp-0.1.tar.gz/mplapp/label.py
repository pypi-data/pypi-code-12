from mplapp.base import Base


class Label(Base):
    """
    A text label.
    """

    def __init__(self, width, height, text, **kwargs):

        self._str = text
        self._width = float(width)
        self._height = float(height)
        self._kwargs = kwargs

        self._text = None
        self._axes = None
        self._colors = ()


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


    def text(self, new_text = None):

        if new_text is None:

            if self._text is None:
                return self._str

            return self._text.get_text()

        else:

            if self._text is None:
                self._str = new_text
            else:
                self._text.set_text(new_text)
                self.canvas().draw()


    def _render(self, fig, x, y):

        # convert size to percent of figure

        W, H = fig.get_size_inches()

        x /= W
        y /= H

        w = self._width / W
        h = self._height / H

        ax = fig.add_axes([x, y, w, h], xticks=[], yticks=[])
        ax.set_xlim([0, self._width])
        ax.set_ylim([0, self._height])

        # background color of label: facecolor

        fc = fig.get_facecolor()

        if 'fc' in self._kwargs:
            fc = self._kwargs['fc']
            del self._kwargs['fc']

        elif 'facecolor' in self._kwargs:
            fc = self._kwargs['facecolor']
            del self._kwargs['facecolor']

        ax.set_axis_bgcolor(fc)

        # edge color of label: edgecolor

        ec = fc

        if 'ec' in self._kwargs:
            ec = self._kwargs['ec']
            del self._kwargs['ec']

        elif 'edgecolor' in self._kwargs:
            ec = self._kwargs['edgecolor']
            del self._kwargs['edgecolor']

        for side in ['bottom', 'top', 'left', 'right']:
            ax.spines[side].set_color(ec)

        # text color of label

        color = 'black'

        if 'color' in self._kwargs:
            color = self._kwargs['color']

        self._colors = (ec, fc, color)

        # defaults

        ha = 'center'
        va = 'center'

        if 'ha' in self._kwargs:
            ha = self._kwargs['ha']

        elif 'horizontalalignment' in self._kwargs:
            ha = self._kwargs['horizontalalignment']

        else:
            self._kwargs['ha'] = ha

        if 'va' in self._kwargs:
            va = self._kwargs['va']

        if 'verticalalignment' in self._kwargs:
            va = self._kwargs['verticalalignment']

        else:
            self._kwargs['va'] = va

        # based on alignment, set x,y

        ha_to_x = dict(
            center = self._width / 2.0,
            left = 0.0,
            right = self._width)

        va_to_y = dict(
            center = self._height / 2,
            top = self._height,
            bottom = 0.0)

        x = ha_to_x[ha]
        y = va_to_y[va]

        self._text = ax.text(x, y, self._str, **self._kwargs)

        self._str = None

        self._axes = ax



