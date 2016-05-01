from mplapp.base import Base


class HorizontalBox(Base):


    ALIGNMENT = ['top', 'center', 'bottom']


    def __init__(self, **kwargs):
        self._widgets = []
        self._padding = kwargs.get('padding', 0.05)

        va = kwargs.get('va', None)

        if va is None:
            va = kwargs.get('verticalalignment', 'center')

        self._va = va

        self._width = 0
        self._height = 0


    def append(self, *args):
        """
        Append widgets in this horizontal box.  A widget may be followed by a
        string specifying the vertical alignment within this box.  Valid
        values include ['top', 'center', 'bottom'], the default is 'center'.
        """

        N = len(args)

        i = 0

        while i < N:

            widget = args[i]

            if i + 1 < N and isinstance(args[i + 1], str):
                va = args[i + 1]

                if va not in self.ALIGNMENT:
                    raise ValueError('invalid alignment "%s"' % va)

                i += 2

            else:
                va = self._va

                i += 1

            w, h = widget.size()

            self._width += w + self._padding
            self._height = max(self._height, h)

            self._widgets.append( (widget, va) )


    def axes(self):
        raise RuntimeError('VericalBox does not have an axes')


    def canvas(self):
        raise RuntimeError('VericalBox does not have a canvas')


    def size(self):
        """
        Returns the minimum size of this box in inches.
        """

        return self._width - self._padding, self._height


    def _render(self, fig, x, y):

        for widget, va in self._widgets:

            w, h = widget.size()

            if va == 'bottom':
                widget._render(fig, x, y)

            elif va == 'center':

                delta = self._height - h

                widget._render(fig, x, y + delta / 2.0)

            elif va == 'top':

                delta = self._height - h

                widget._render(fig, x, y + delta)

            x += w + self._padding
