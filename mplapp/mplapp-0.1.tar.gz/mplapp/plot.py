from mplapp.base import Base


class Plot(Base):
    """
    A wrapper for an Axes.
    """

    def __init__(self, width, height, **kwargs):

        self._width = float(width)
        self._height = float(height)
        self._axes = None


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


    def _render(self, fig, x, y):

        # convert size to percent of figure

        W, H = fig.get_size_inches()

        x /= W
        y /= H

        w, h = self.size()

        w /= W
        h /= H

        self._axes = fig.add_axes([x, y, w, h])
