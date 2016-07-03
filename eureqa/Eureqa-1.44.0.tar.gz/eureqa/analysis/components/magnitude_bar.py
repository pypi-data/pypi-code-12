from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class MagnitudeBar(_Component):

    _component_type_str = 'MAGNITUDE_BAR'

    def __init__(self, value=None, color=None, analysis=None, component_id=None, component_type=None):
        """
        Magnitude Bar: implements a visual representation of percentages

        Common/expected usage is as follows:

        >>> pink_bar = MagnitudeBar(value=-0.22, color='#ff00ff')
        >>> card = analysis.create_html_card("Here is the magnitude bar: {0}".format(analysis.html_ref(pink_bar)))


        :param float value: value expressed by this MagnitudeBar
        :param str color (optional): color to use for the magnitude bar instead of default
        :param ~eureqa.analysis.Analysis analysis: (optional) Analysis to associate this Layout with
        :param str component_id: Internal, do not use
        :param str component_type: Internal, do not use
        """
        if value is not None:
            self._value = value

        if color is not None:
            self._color = color

        super(MagnitudeBar, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

    @property
    def value(self):
        """The value expressed by this MagnitudeBar.
        Must be a fractional number between 0 and 1 (positive bar) or 0 and -1 (negative bar).

        :rtype: float
        """
        return getattr(self, "_value", None)

    @value.setter
    def value(self, val):
        self._value = val
        self._update()

    @property
    def color(self):
        """The Color of this bar, expressed as an html hex color code.

        For example: '#ff5733' - red

        :rtype: str
        """
        return getattr(self, "_color", None)

    @color.setter
    def color(self, val):
        self._color = val
        self._update()

    def _fields(self):
        return super(MagnitudeBar, self)._fields() + [ 'value', 'color' ]
