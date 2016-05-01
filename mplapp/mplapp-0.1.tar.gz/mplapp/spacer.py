from mplapp.base import Base


class Spacer(Base):
    """
    Just something that takes up space, to aid widget alignment.
    """

    def __init__(self, width, height):

        self._width = float(width)
        self._height = float(height)


    def axes(self):
        raise RuntimeError("Spacer does not have an axes")


    def canvas(self):
        raise RuntimeError("Spacer does not have a canvas")


    def size(self):
        return (self._width, self._height)


    def _render(self, fig, x, y):
        pass