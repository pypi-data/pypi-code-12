from eureqa.analysis.components.base import _Component

class Tooltip(_Component):

    _component_type_str = 'TOOLTIP'

    def __init__(self, html=None, tooltip=None, analysis=None, component_id=None, component_type=None):
        """
        Tooltip Component: implements a tooltip

        Common/expected usage is as follows:

        >>> tt = Tooltip(html="This", tooltip="Text to show when hovering")
        >>> card = analysis.create_html_card("This is a component with a tooltip: {0}".format(analysis.html_ref(tt)))


        :param str html: Text to display normally
        :param str tooltip: The tooltip text to show when the cursor hovers over the component
        :param ~eureqa.analysis.Analysis analysis: (optional) Analysis to associate this Layout with
        :param str component_id: Internal, do not use
        :param str component_type: Internal, do not use
        """

        super(Tooltip, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

        if html is not None:
            self._text = html

        if tooltip is not None:
            self._tooltip_content = tooltip


    @property
    def html(self):
        """The text to show normally for this component.

        :rtype: str
        """
        return self._text

    @html.setter
    def html(self, val):
        self._text = val
        self._update()


    @property
    def tooltip(self):
        """The tooltip text to show when the cursor hovers over the component

        :rtype: str
        """
        return self._tooltip_content

    @tooltip.setter
    def tooltip(self, val):
        self._tooltip_content = val
        self._update()



    def _fields(self):
        return super(Tooltip, self)._fields() + [ 'text', 'tooltip_content' ]
