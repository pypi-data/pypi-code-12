from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class TabbedLayout(_Component):

    _component_type_str = 'TABBED_LAYOUT'

    def __init__(self, tabs=None, analysis=None, component_id=None, component_type=None):
        super(TabbedLayout, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)
        if analysis is not None:
            _JsonREST.__init__(self, analysis._eureqa)
            self._analysis = analysis

        if tabs is not None:
            self._tabs = tabs


    @property
    def tabs(self):
        return self._tabs

    @tabs.setter
    def tabs(self, val):
        self._tabs = val
        self._update()

        

    def _fields(self):
        return super(TabbedLayout, self)._fields() + [ 'tabs' ]

