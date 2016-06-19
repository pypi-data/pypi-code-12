from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class Tooltip(_Component):

    _component_type_str = 'TOOLTIP'

    def __init__(self, analysis=None, component_id=None, component_type=None, text=None, tooltip_content=None):
        super(Tooltip, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)
        if analysis is not None:
            _JsonREST.__init__(self, analysis._eureqa)
            self._analysis = analysis

        if text is not None:
            self._text = text

        if tooltip_content is not None:
            self._tooltip_content = tooltip_content


    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        self._text = val
        self._update()

        
    @property
    def tooltip_content(self):
        return self._tooltip_content

    @tooltip_content.setter
    def tooltip_content(self, val):
        self._tooltip_content = val
        self._update()

        

    def _fields(self):
        return super(Tooltip, self)._fields() + [ 'text', 'tooltip_content' ]

