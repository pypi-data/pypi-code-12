from mplapp.base import Base


class VerticalBox(Base):

    ALIGNMENT = ['left', 'center', 'right']

    def __init__(self, **kwargs):
        self._widgets = []
        self._padding = kwargs.get('padding', 0.05)

        ha = kwargs.get('ha', None)

        if ha is None:
            ha = kwargs.get('verticalalignment', 'center')

        self._ha = ha

        self._width = 0
        self._height = 0


    def append(self, *args):
        """
        Append widgets in this vertical box.  A widget may be followed by a
        string specifying the horizontal alignment within this box.  Valid
        values include ['left', 'center', 'right'], the default is 'center'.
        """

        N = len(args)

        i = 0

        while i < N:

            widget = args[i]

            if i + 1 < N and isinstance(args[i + 1], str):
                ha = args[i + 1]

                if ha not in self.ALIGNMENT:
                    raise ValueError('invalid alignment "%s"' % ha)

                i += 2

            else:
                ha = self._ha

                i += 1

            w, h = widget.size()

            self._width = max(self._width, w)

            self._height += h + self._padding

            self._widgets.append( (widget, ha) )


    def axes(self):
        raise RuntimeError('VericalBox does not have an axes')


    def canvas(self):
        raise RuntimeError('VericalBox does not have a canvas')


    def size(self):
        """
        Returns the minimum size of this box in inches.
        """

        return self._width, self._height - self._padding


    def _render(self, fig, x, y):

        for widget, ha in self._widgets[::-1]:

            w, h = widget.size()

            if ha == 'left':
                widget._render(fig, x, y)

            elif ha == 'center':

                delta = self._width - w

                widget._render(fig, x + delta / 2.0, y)

            elif ha == 'right':

                delta = self._width - w

                widget._render(fig, x + delta, y)

            y += h + self._padding
